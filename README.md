# ldap-sync-memberof

A simple Python script that stores a user's `posixGroup` memberships against their `memberOf` attribute.

* It is a requirement that a given user have the `inetOrgPerson` object class for the `memberOf` sync to work.
* The script will add the `inetUser` object class if the user doesn't have it.

## How It Works
It first queries all `posixGroup` objects for their `memberUid` field, it then aggregates all the results together in the following structure:

```
{
  'memberUid-1': [
    'cn=email_user,ou=Groups,dc=domain,dc=com',
    'cn=pc_user,ou=Groups,dc=domain,dc=com',
    'cn=phone_user,ou=Groups,dc=domain,dc=com'
  ],
  'memberUid-2': [
    'cn=email_user,ou=Groups,dc=domain,dc=com',  
  ]
}
```

It then populates the `memberOf` attribute of each listed user in the aggregation.

**Warning: the `memberOf` attribute is available in the `inetUser` object class, this script will attempt to add this object class to any user without it automatically.**

## Installation

```
$ git clone https://github.com/DeBortoliWines/ldap-sync-memberof.git
$ cd ldap-sync-memberof
$ pip install -r requirements.txt
```

## Usage

```
usage: main.py [-h] [-D USER_DN] -P PASSWORD_FILE -s LDAP_SERVER

Syncs memberOf attribute onto users that are in posixGroups. Adds `inetUser`
object class to the users if they don't already have it.

optional arguments:
  -h, --help            show this help message and exit
  -D USER_DN, --user-dn USER_DN
                        The user DN with correct permissions, such as
                        Directory Manager.
  -P PASSWORD_FILE, --password-file PASSWORD_FILE
                        Password file that has the password in plaintext for
                        the given user.
  -s LDAP_SERVER, --ldap-server LDAP_SERVER
                        LDAP server hostname.
```

## License
Tool licensed under Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0). See the [LICENSE](/LICENSE) file.
