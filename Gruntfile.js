module.exports = function(grunt) {

    grunt.initConfig({
        run_grunt: {
            pbc: {
                src: ['node_modules/pbs/Gruntfile.js']
            }
        },
        watch: {
            pbc: {
                files: ['node_modules/pbs/**/*'],
                tasks: ['run_grunt']
            }
        },
        curl: {
            'pb/static/hack/asciinema.css': 'https://raw.githubusercontent.com/ptpb/pb-asciinema/master/css/main.css',
            'pb/static/hack/asciinema.js': 'https://raw.githubusercontent.com/ptpb/pb-asciinema/master/js/release.js'
        }
    });

    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-run-grunt');
    grunt.loadNpmTasks('grunt-curl');

    grunt.registerTask('default', ['run_grunt', 'curl']);
}
