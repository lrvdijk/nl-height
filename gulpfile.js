fs = require("fs");
path = require("path");
http = require("http");

// Required Gulp modules
var gulp = require('gulp');
var gutil = require('gulp-util');

var coffee = require('gulp-coffee');
var concat = require('gulp-concat');
var cssnano = require('gulp-cssnano');
var preprocess = require('gulp-preprocess');
var sourcemaps = require('gulp-sourcemaps');

var livereload = require('gulp-livereload');
var connect = require("connect");
var connect_lr = require("connect-livereload");
var serve_static = require("serve-static");

var environments = require('gulp-environments');
var development = environments.development;
var production = environments.production;

// Configuration
var APP_DIR = './app/';
var COFFEESCRIPT_DIR = APP_DIR + 'coffee/';
var BUILD_DIR = './build/';


var currentBuildDir = function() {
    return BUILD_DIR + environments.current().$name + '/';
};

String.prototype.endsWith = function (searchString, position) {
    var lastIndex, subjectString;
    subjectString = this.toString();
    if (typeof position !== 'number' || !isFinite(position) || Math.floor(position) !== position || position > subjectString.length) {
        position = subjectString.length;
    }
    position -= searchString.length;
    lastIndex = subjectString.indexOf(searchString, position);
    return lastIndex !== -1 && lastIndex === position;
};

var getLocations = function() {
    locations = {};
    files = fs.readdirSync(currentBuildDir() + 'data/');

    for(key in files) {
        file = files[key];
        filepath = path.join(currentBuildDir(), 'data', file);

        if(fs.lstatSync(filepath).isDirectory()) {
            metadata_path = path.join(filepath, 'metadata.json');
            if(fs.lstatSync(metadata_path).isFile()) {
                metadata = JSON.parse(String(fs.readFileSync(metadata_path)));
                metadata.properties['slug'] = file;
                metadata.properties['metadata_file'] = metadata_path.replace(
                    currentBuildDir().slice(1), "");

                locations[file] = metadata;
            }
        }
    }

    return locations
};

var locationsStream = function() {
    var src = require('stream').Readable({objectMode: true});
    src._read = function() {
        this.push(new gutil.File({
            cwd: "",
            base: "",
            path: "locations.json",
            contents: new Buffer(JSON.stringify(getLocations()))
        }));

        this.push(null);
    };

    return src;
};


// Start of Gulp tasks
gulp.task('compile-coffee', function () {
    return gulp.src(COFFEESCRIPT_DIR + '**/*.coffee')
        .pipe(coffee({'bare': true}))
        .on('error', gutil.log)
        .pipe(gulp.dest(APP_DIR + 'js/'))
        .pipe(livereload());
});

gulp.task('build-app-js', ['compile-coffee'], function () {
    return gulp.src(APP_DIR + 'js/**/*.js')
        .pipe(sourcemaps.init())
        .pipe(concat('seahouse.js'))
        .pipe(sourcemaps.write('./maps'))
        .pipe(gulp.dest(currentBuildDir() + 'js/'))
        .pipe(livereload())
});

gulp.task('build-app-html', function () {
    return gulp.src(APP_DIR + '*.html')
        .pipe(preprocess({
            NODE_ENV: environments.current().$name
        }))
        .pipe(gulp.dest(currentBuildDir()))
        .pipe(livereload())
});

gulp.task('build-app-css', function () {
    return gulp.src(APP_DIR + 'css/**/*.css')
        .pipe(development(sourcemaps.init()))
        .pipe(concat('seahouse.css'))
        .pipe(production(cssnano()))
        .pipe(gulp.dest(currentBuildDir() + 'css/'))
        .pipe(livereload())
});

gulp.task('build-app-img', function () {
    return gulp.src(APP_DIR + 'img/**/*')
        .pipe(gulp.dest(currentBuildDir() + 'img/'))
        .pipe(livereload())
});

gulp.task('build-datasets', function() {
    return gulp.src('./data/json/**/*')
        .pipe(gulp.dest(currentBuildDir() + 'data/'))
        .pipe(livereload())
});

gulp.task('build-locations', function() {
    if(production()) {
        locationsStream()
            .pipe(gulp.dest(currentBuildDir() + 'data/'))
    }
});

gulp.task('build', [
    'build-app-js', 'build-app-html', 'build-app-css', 'build-app-img', 'build-datasets', 'build-locations'
]);

gulp.task('watch-coffee', function () {
    return gulp.watch(COFFEESCRIPT_DIR + '**/*.coffee', ['compile-coffee']);
});

gulp.task('watch-html', function () {
    return gulp.watch(APP_DIR + '*.html', ['build-app-html']);
});

gulp.task('watch-js', function () {
    return gulp.watch(APP_DIR + 'js/**/*.js', ['build-app-js']);
});

gulp.task('watch-css', function () {
    return gulp.watch(APP_DIR + 'css/**/*.css', ['build-app-css']);
});

gulp.task('watch-img', function () {
    return gulp.watch(APP_DIR + 'img/**/*', ['build-app-img']);
});

gulp.task('watch-dataset', function() {
    return gulp.watch(APP_DIR + 'data/json', ['build-datasets']);
});

gulp.task('watch', [
    'watch-coffee', 'watch-html', 'watch-js', 'watch-css', 'watch-img',
]);


// Server configuration, make sure the browser decompresses the gzipped JSON
var serve = serve_static(currentBuildDir(), {
    setHeaders: function (res, path) {
        if (path.endsWith(".json.gz")) {
            res.setHeader("Content-Type", "application/json");
            res.setHeader("Content-Encoding", "gzip");
        }
    }
});


var listLocations = function(req, res, next) {
    locations = getLocations();

    res.statusCode = 200;
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.end(JSON.stringify(locations));
};

gulp.task('serve', ['build'], function (done) {
    app = connect();
    app.use('/data/locations.json', listLocations);
    app.use(connect_lr({
        port: 35729,
        ignore: ['.gz', '.js', '.json']
    }));
    app.use(serve);

    console.log("Serving on 8080");

    server = http.createServer(app);
    server.listen(8080, done);
    livereload.listen({start: true})
    console.log("Serving on 8080");
});

gulp.task('default', ['watch', 'serve']);
