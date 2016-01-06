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
            'pb/static/hack/asciinema.css': 'https://github.com/asciinema/asciinema-player/releases/download/v2.0.0/asciinema-player.css',
            'pb/static/hack/asciinema.js': 'https://github.com/asciinema/asciinema-player/releases/download/v2.0.0/asciinema-player.js'
        }
    });

    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-run-grunt');
    grunt.loadNpmTasks('grunt-curl');

    grunt.registerTask('default', ['run_grunt', 'curl']);
}
