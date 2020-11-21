[![General Assembly Logo](https://camo.githubusercontent.com/1a91b05b8f4d44b5bbfb83abac2b0996d8e26c92/687474703a2f2f692e696d6775722e636f6d2f6b6538555354712e706e67)](https://generalassemb.ly/education/web-development-immersive)

# Django Auth

When working with any framework, we may want to implement Authorization and Authentication.

## Prerequisites

- [django-relationships](https://git.generalassemb.ly/ga-wdi-boston/django-relationships)

## Objectives

By the end of this, developers should be able to:

- Explain the built-in user authentication in Django
- Explain the code for a custom user model
- Manage view permissions
- Manage resource "ownership"

## Preparation

1. Fork and clone this repository.
 [FAQ](https://git.generalassemb.ly/ga-wdi-boston/meta/wiki/ForkAndClone)
1. Create and checkout to a new branch, `training`, for your work.
1. Run `pipenv shell` to start up your virtual environment.
2. Run `pipenv install` to install dependencies.
3. Create a psql database for the project
    1. Type `psql` to get into interactive shell
    2. Run `CREATE DATABASE "django_mangos_auth";`
    3. Exit shell
4. Run migrations with `python manage.py migrate`
1. Open the repository in Atom with `atom .`

## Defining Authentication and Permissions Classes

So far we have looked at making Django APIs that do not include any user
ownership or even a way for a user to sign in! Time to change that.

This repository contains a basic API for `mangos` - no resource ownership or
user authentication included.

We can set up what kind of authentication we want to use by either declaring
global defaults for our project or by attaching individual authentication
classes to individual views. These authentication classes are provided by
Django and give us different abilities.

If we go into our `settings.py` file, we can add defaults across our project by
using the `REST_FRAMEWORK` object. Below, this code is telling the project to
use `TokenAuthentication` by default.

```py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication'
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ]
}
```

We could also attach authentication classes to individual views like this:

```py
class ExampleView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated,]
```

There are a lot of these classes and can all be found in the
[DRF authentication documentation](https://www.django-rest-framework.org/api-guide/authentication/).

Setting up our authentication and permissions either globally or on individual
viewsets will set up those routes to either allow or prevent access without
proper authentication. This will also give us some extra information on our
`request` object inside our routes. In our case with `TokenAuthentication`, we
will be given a `request.user` and `request.auth`. These objects will be what
allow us to implement user ownership.

### TokenAuthentication

Remember how we used tokens in our JavaScript clients and Express APIs? Token
authentication works by having the client request a token on something like a
user login. The client stores the token, then sends it in requests so the API
knows who is making that request. Then, the API can use the token to check if
the user has the correct permissions to do what they're doing.

By using the [`TokenAuthentication` class](https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication) from the Django
Rest Framework, we will be able to authenticate users based on the token they
send in their requests. Then, we will be able to set permission classes on our
views, such as `IsAuthenticated` to ensure we get a proper token in the
request. If we do, we will have access to a `user` object and `auth` token on
the `request` object.

## Annotate-Along: Creating a Custom User

While it's not _technically_ required to create a custom `User` model, it is
**highly recommended** by both the Django community and the [Django documentation itself](https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project).

This model will behave very similar to the baked-in user model that Django
provides, but we will be able to customize it to fit our needs in the future
without worrying about a lot of [re-migrating and database-dropping](https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#changing-to-a-custom-user-model-mid-project).

**Step One: Custom User Model**

Open the file in the `models` folder for our user model called `user.py`.
Here, the user model inherits from the `AbstractBaseUser` and uses an
email field in place of the username. The `__str__` method of our user model
returns their email.

**Step Two: Custom User Model Manager**

There is also a custom class that overrides the built-in `UserManager` for
the User model. This is recommended by Django in the case that we change any of
the fields on our model, which we do.

**Step Three: Custom User Model Registration**

Finally, we tell our project about this new `User` model by adding
`AUTH_USER_MODEL` in `settings.py`.

**Step Four: Custom `User` Admin Forms**

If you look at the `admin.py` file in this repo, you'll see some extra code
that we don't normally need for our custom resources. This code is specifically
modifying the already baked-in forms for Django's admin content management
system. These forms assume the user has certain data. When we change that data
by building our custom user model, we also need to change the forms.

## Code-Along: Using the Custom User

Let's double-check that all of this works so far.

1. Make sure you ran your migrations
2. Create superuser
3. Run server
4. Navigate to admin view and login

## User Routes

Time to get our user working as it should for our API. We want users to be able
to sign in, sign up, change their password, and log out.

### Code-Along: Sign Up

For sign up, we will be creating a new user. This will require us to create a
`UserSerializer` and `UserRegisterSerializer` to handle what happens to our
data on create.

Our sign up view class will inherit from `generics.CreateAPIView` and will only
support a `post` method. In that method, we will:

- Check the incoming data with `UserRegisterSerializer`
- If the data is valid, create a new user through the `UserSerializer`
- Check that the created user is valid
    - If no: Respond with a 400 bad request
    - If yes: Respond with a 201 and the newly created user

### Code-Along: Sign In

Signing in requires us to start working with tokens. This class view will also
inherit from `generics.CreateAPIView` support a POST request.

The `django.contrib.auth` library that is included with Django gives us two
important functions for sign in: `authenticate` and `login`. The `authenticate`
method will take our request as well as the user's email and password
combination. Then, as long as our user exists and is active, we will use
`login` to log them in!

The response should include a token, so we will add a method on the `User`
model to handle getting a new token. This method will clear out the previous
token so that every time we sign in we have a new token for our requests.

### Lab: SignOut

Use the documentaiton to conquer signing out on your own. You will need:

- To create a new class view called `SignOut` that extends from an API view for deleting
- Add a `delete` method to the class which:
    - Calls a new, custom model method that deletes the token
    - Calls the `logout` method
    - Returns a empty `200` response on success

### Code-Along: Change Password

The `ChangePassword` class is going to inherit from `generics.UpdateAPIView`
and use the `partial_update` method to perform this change. We will need to
create a `ChangePasswordSerializer` that will accept a `new` and `old` password.

We can use `check_password` method on the user object to compare the old
password provided with the actual password stored on the user. Then, we can
update the password using the `set_password` method. Finally, we will save the
updated user and send a long an empty `200` response.

## User Ownership

### Code-Along: The Mango Model

To complete user ownership, we will have to set up a relationship between our
`Mango`s and our `User`s.

1. Add a `ForeignKey` to the `Mango` model
2. Run migrations

### Code-Along: `Create`

To get started, we need to add a `permission_classes` definition to our view
class. This will prevent users from accessing these views without sending along
a token.

Let's fill in the `post` method in the `Mangos` view. We will need to use the
`request.user.id` to set the `owner` property on the data we send the
`MangoSerializer`.

### Code-Along: `Show`

For the `show` method, we need to make sure the user owns the mango they want
to see. To do this, we can compare the `owner` of the mango against the
`request.user.id` value. If they don't have permission, we can throw a
permissions error.

### Lab: `Index`, `Update`, and `Delete`

**Index**

The index method is the `get` method in the `Mangos` class. This method should
`filter` out only the mangos that the signed-in user owns and return that list.

**Update**

The update method is the `partial_update` method in the `MangosDetail` class.
This method should check if the incoming data has an `owner` key on it, and
remove it if it does. Then, it will find the mango, check that the user owns
it, and add the `request.user.id` onto the request object to be serialized.
Finally, after the serialized mango is updated it should be saved and returned
to the client.

**Delete**

The `delete` method lives in the `MangosDetail` class. Ensure the user owns the
mango they are trying to delete, then `delete()` it.

## Additional Resources

- [Django Rest Framework Tutorial: Authentication](https://www.django-rest-framework.org/api-guide/authentication)

## [License](LICENSE)

1. All content is licensed under a CC­BY­NC­SA 4.0 license.
1. All software code is licensed under GNU GPLv3. For commercial use or
    alternative licensing, please contact legal@ga.co.
