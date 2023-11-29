# Project Name
- Isaac (@isaac-h-chan)
- Kathy (@crxbun) - TEAM LEAD
- Caroline (@Caroline-Zana)

- Duy (@Duy-Nguyen012)
+ Update User Profile
@flask_obj.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    Allow user to edit the user profile like email, username and password
        Parameters:
            None
        Returns:
            redirect (update_profile.html): to update the profile 
+ Convert Note into pdf
flask_obj.route("/download/<int:note_id>", methods=["POST"])
def convert(note_id):
    Allow user to download the note that they choose
        Parameters:
            note_id
        Returns:
            return send_file(pdf_path, as_attachment=True,download_name=pdf_filename) : generate the pdf file and store into your local device

