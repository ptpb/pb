## pb

pb is a lightweight pastebin built using Flask. pb supports both standard form input, as well as raw input for arbitrary data. pb was written to be easy to deploy, so please feel free to host your own pb instance. The official instance of pb can be found at [ptpb.pw](https://ptpb.pw).

### Use

From the Web: [Paste](https://ptpb.pw)

Command Line (non-raw):
`yourcommand | curl -F "c=<-" https://ptpb.pw`

Command Line (raw):
`yourcommand | curl --data-binary '@-' https://ptpb.pw/r`

Alias (non-raw):
`alias ptpb='curl -F "c=<-" https://ptpb.pw` 

Add alias to `~/.bashrc` to use:
`yourcommand | ptpb`

### Installation

1. Install the requirements (located in requirements.txt) `pip install -r requirements.txt`
2. Create a database for pb, add a user with all privileges on said database. 
3. Copy the example config to config.yaml, input a secret key and your database information.
4. Start pb. You can use the built in Flask server (not recommended) by running: `python pb.py`, we recommend using [Gunicorn](https://github.com/benoitc/gunicorn)

### Endpoints

* / - View index, handle all form post data
* /f - Returns the form
* /s - Returns the number of pastes 
* /r - Handle raw post data
* /p/<id> - View paste with <id>
