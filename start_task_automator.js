// Includes 
const cron = require("node-cron");
var shell = require("shelljs");
const yargs = require('yargs');
var fs = require('fs');

const argv = yargs.option('spec',{
    alias: 's',
    type: 'string',
    description: 'Spec file to run the task automator'
}).help().alias('help','h').argv;

var task = cron.schedule('* * 8 * * 0', () => {
    //get the name of the spec file.
    const filename = argv.spec || "task_automator_specs.json";
    var spec_data_string; 
    fs.readFile(filename,function(err,data){
        if (err){
            console.log(err);
            throw err;
        }
        spec_data_string = data;
        // debug info 
        console.log(spec_data_string); 
    });
    var spec_data_json; 
    try{
        spec_data_json = JSON.parse(spec_data_string);
    }catch(SyntaxError){
        console.log("Problem parsing json")
    }
    var project = spec_data_json.project;
    var section = spec_data_json.section; 
    var task_automator_options = "SETUP";
    if(project != null){
        task_automator_options += "-p " + project; 
    }
    if(section != null){
        task_automator_options += "-s " + section;
    }
    console.log("Entering python environment ...");
    var status = shell.exec("source bin/activate").code;
    if(status != 0){
        console.log("There was problem entering the python environment")
    }
    console.log("Preparing taskAutomator ...");
    

    console.log("Running taskAutomator");
    status = shell.exec("python3 taskClient.py").code;
    if(status != 0){
        console.log("There was a problem running the taskClient");
    }
    console.log("Success running taskAutomator");
    console.log("Deactivating python environment");
    status = shell.exec("deactivate");
    if(status != 0){
        console.log("Problem deactivating environment")
    }
});

task.start();

