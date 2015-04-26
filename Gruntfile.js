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
        }
    });

    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-run-grunt');

    grunt.registerTask('default', ['run_grunt']);
}
