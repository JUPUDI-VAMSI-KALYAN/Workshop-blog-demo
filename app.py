from flask import Flask, render_template, request, redirect, url_for
from ibm_cloud_sdk_core import ApiException
from ibmcloudant.cloudant_v1 import CloudantV1, Document
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import json

app = Flask(__name__)

# Load Cloudant credentials from JSON
with open('cloudant_credentials.json') as f:
    cloudant_credentials = json.load(f)

# Create IAM authenticator
authenticator = IAMAuthenticator(cloudant_credentials['apikey'])

service = CloudantV1(authenticator=authenticator)

service.set_service_url(cloudant_credentials['url'])

response = service.get_server_information().get_result()
print("-----Server information------")
print(response)
print("-----all dbs------")

response = service.get_all_dbs().get_result()

print(response)
print("----------------------")

# Initialize the database
db_name = 'workshop_db'
# Try to create database if it doesn't exist
try:
    put_database_result = service.put_database(
        db=db_name
    ).get_result()
    if put_database_result["ok"]:
        print(f'"{db_name}" database created.')
except ApiException as ae:
    if ae.status_code == 412:
        print(f'Cannot create "{db_name}" database, ' +
              'it already exists.')
        
print("-----Database is Ready------")



print(response)




# Home page route
# print(document)
@app.route('/')
def home():
    posts = []
    response = service.post_changes(
            db=db_name
            ).get_result()
    for e in response['results']:
        print(e["id"])
        document = service.get_document(
            db=db_name,
            doc_id= e["id"]
        ).get_result()
        print(f'Document retrieved from database:\n'
      f'{json.dumps(document, indent=2)}')
        posts.append(document)
    return render_template('index.html', posts=posts)

    

    
    


#     posts = service.post_all_docs(
#         db=db_name,
#         include_docs=True,
#         start_key='abc',
#         limit=10
#         ).get_result()
#     print(posts)
#     

# @app.route('/')
# def home():
#     # Retrieve posts from wherever they are stored
#     posts = [
#         {'title': 'First Post', 'content': 'This is the content of the first post.'},
#         {'title': 'Second Post', 'content': 'This is the content of the second post.'}
#     ]
#     return render_template('index.html', posts=posts)

# Route to create new post
@app.route('/create', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':

        example_document: Document = Document()
        # Add "name" and "joined" fields to the document
        example_document.title = request.form['title']
        example_document.content = request.form['content']

        # Save the document in the database with "post_document" function
        try:
            create_document_response = service.post_document(
                db=db_name,
                document=example_document
            ).get_result()

            print("--- document created ---")
            return redirect(url_for('home'))
        except ApiException as ae:
            print(ae)
        

    return render_template('create.html')

if __name__ == '__main__':
    app.run(debug=True)
