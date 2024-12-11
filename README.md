# Dream Machine

An interactive dream script generator that creates unique, playable dream scenarios using AI.

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/gracelynxs/DreamMachine.git
cd DreamMachine
```

### 2. Create Environment File
Request the `.env` file from the project maintainer and place it in the root directory of your local repository.

### 3. Set Up Virtual Environment

#### For Mac/Linux:
```bash
python -m venv venv
source venv/bin/activate
```

#### For Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
Note: If you get a PowerShell execution policy error, run `Set-ExecutionPolicy RemoteSigned` as Administrator first.

#### For Windows (Command Prompt):
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

### 4. Install Requirements
```bash
pip install -r requirements.txt
```
### 5. Replace this in main.py
```if __name__ == '__main__':
  app.run(debug=True)
```
with
```if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)
```

   
### 5. Run the Application
```bash
python main.py
```
The application will be available at `http://127.0.0.1:5000`

## Requirements
- Python 3.7+
- `.env` file (provided by maintainer)
