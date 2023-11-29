# Mintnote
- Isaac (@isaac-h-chan)
- Kathy (@crxbun) - TEAM LEAD
- Caroline (@Caroline-Zana)

- Duy (@Duy-Nguyen012)

## How to Run
1. Pull the repository
2. Install all required python packages using the following command in terminal
```
pip install -r requirements.txt
```
3. macOS/Linux: Start the website by running the following command
```
python3 run.py
```
3. Windows: Start the website by running the following command
```
python run.py
```
4. Go to [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in a web browser such as Chrome or Firefox

+ Update User Profile
```
@flask_obj.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    Allow user to edit the user profile like email, username and password
        Parameters:
            None
        Returns:
            redirect (update_profile.html): to update the profile
```
+ Convert Note into pdf
```
flask_obj.route("/download/<int:note_id>", methods=["POST"])
def convert(note_id):
    Allow user to download the note that they choose
        Parameters:
            note_id
        Returns:
            return send_file(pdf_path, as_attachment=True,download_name=pdf_filename) : generate the pdf file and store into your local device
```

