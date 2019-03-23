# Task Description
Development of a web application with the API for the comment service.
# Requirements
1. Each comment is connected with specific user. 
2. Comments can be edited and deleted. 
3. Removal of comment is possible only if this comment has no chid comments.
4. Each comment is characterized by date and time of creation and latest patch. 
5. Comments have a tree structure.
6. Each comment belongs to specific entity (blog post, news page, other comment etc.) which is uniquely identified by a pair of values (entity type ID, entity ID).
7. The API must provide the following interfaces: 
    1. Creation of a comment for a specific entity;
    2. Editing a comment by ID;
    3. Getting first level comments for a specific entity with pagination;
    4. Getting all child comments for a given comment with no nesting level limit. The response must be such that clients comments hierarchy can be recreated;
    5. Uploading to the file the entire history of comments on the user with the ability to specify the time interval in which the user comment was created. The response time to the primary query should not depend on the amount of data in the final upload;
    6. Opportunity to view the history of all user uploads with the ability to re-load the same data.

## Additional Requirements

1. Storage of the historical data (information about by whom and when the comment was edited/created, what exactly was changed in the comment).
2. The ability to subscribe to commenting events of a specific entity (when comment is created/edited/deleted to this entity, the server sends PUSH notification to user with information about created/edited/deleted comment).
3. For the first point of Additional Requirements to implement a flexible method with ability to add different file extensions. 

# Solution Description

Used technical means:
+ Python 3.6;
+ Django rest framework;
+ Django framework;
+ Django channel;
+ Celery.

For implementation of tree of comments storage I used SQL anti-pattern Closure Table. Its advantages include the ease of reading and writing the comment tree what allows use Django ORM and there is no need to write native SQL. No need for recursive queries allowing you to select different types of relational databases. Disadvantages include the fact that the hierarchy of comments is stored in a separate table and it is necessary to store in this table the relationships of each element of the tree with its ancestors as well as the reference of each element to itself, which can be redundant

The mechanism of uploading historical data to the file was divided into two parts:

1. Creating a record in the database with selected conditions of uploading and future filename;
2. Creating file.

For the second point, async task that is processed in celery is used. Upon completion of the task, the user receives a PUSH notification with the flag of the created file. 

To implement notification on creating/deleting/editing a comment, the Channel library is used. Sending notifications is carried out using a function send_notification, which is used in all Views where operations on creating/deleting/editing comments happen.

# API methods description
1. Methods of working with comments:
    + api/comments/list/\<int:content_type_id\>/\<int:object_id\>
        + GET - list of all comments
        + POST - creating a new comment
        
            Request example:
            ```json
            {
              "body": "text"
            }
            ```
    + api/comments/list/\<int:content_type_id\>/\<int:object_id\>/\<int:id\>
        + GET - getting all comment's descendants
        + POST - creating a new child comment
       
          Request example:
          ```json
          {
            "body": "text"
          }
          ```
        
    + api/comments/detail/\<int:id\>
        + DELETE - deleting comment
        + PUT - editing comment
          
          Request example:
          ```json
          {
            "body": "edited text"
          }
          ```
2. Methods of working with posts(News, Blogs)
    + api/posts/news/list
        + GET - getting list of news
    + api/posts/news/detail/\<int:id\>
        + GET - getting a separate news
    + api/posts/blogs/list
        + GET - getting list of blogs
    + api/posts/blogs/detail/\<int:id\>
        + GET - getting a separate blog
3. Methods of working with users
    + api/accounts/auth/login
        + POST - login
        
        Request example:
        ```json
          {
            "username": "admin",
            "password": "somePwd123"
          }
         ```
    + api/accounts/auth/logout
        + POST - logout
    + api/accounts/register
        + POST - creating user
        Request example:
        ```json
          {
            "username": "admin",
            "email": "test@test.test",
            "password1": "somePwd123",
            "password2": "somePwd123"
          }
        ```
4. Methods of working with comment reports
    + api/comments/reports/lis
        + GET - getting list of reports
        + POST - creating new report
            
            Request example:
          ```json
          {
            "date_from": "01.01.2000",
            "date_till": "01.01.2019",
            "format": "json",
            "content_type_id": 10,
            "object_id": 1
          }
          ```