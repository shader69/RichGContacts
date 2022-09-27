# RichGContacts
RichGContacts is a tool that allow you to synchronize social networks data with your associated Google Contact.
- You will always have an updated contact picture of your friends
- You won't forget their dates of birth

### Managed social networks :
- Instagram
- Facebook (not working yet)

## 💡 Prerequisite
- [Python 3](https://www.python.org/downloads/release/python-370/)
- [Google Developer Account](https://console.cloud.google.com/), for manage API access
- [Google account](https://myaccount.google.com/), for manage contacts

## 🛠️ Installation
### Use Github to install the project

```bash
git clone https://github.com/shader69/richgcontacts.git
cd richgcontacts/
python3 setup.py install
```

### Prepare your Google Cloud workspace
- Go to [Google Cloud Console](https://console.cloud.google.com/) > [APIs and services section](https://console.cloud.google.com/apis/dashboard).
- Activate [People API](https://console.cloud.google.com/apis/api/people.googleapis.com/).
- Go to [Credentials section](https://console.cloud.google.com/apis/credentials), and create an **ID OAuth 2.0** key.
- Get the **credentials.json** file, and copy it into project **data** folder.

### Prepare your Google Account to manage
- Go to your [contacts list](https://contacts.google.com/), with the Google Account to use.
- Choose a contact to manage.
- In your contact data, go on **Instant messages** section, and add a field for each social network you want to sync.
- Try to execute the script: the first run will open a web window. You need to accept the conditions to using the script. After that, the _token.json_ file will be automatically created.

## 📚 Usage:

### Run the app in Python console
```
richgcontacts
```

### Or in Windows CMD
```
python3 project/demo.py
```