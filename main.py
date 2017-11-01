#!/usr/bin/python

import sys
import os
import traceback
import argparse

import ldap3


class Ldap():
    """ Class for containing LDAP connections/operations """

    def __init__(self, server_uri, ldap_user, ldap_pass):
        self.server = ldap3.Server(server_uri, get_info=ldap3.ALL)
        self.conn = ldap3.Connection(self.server, user=ldap_user, password=ldap_pass, auto_bind=True)

    def getGroups(self):
        self.conn.search('dc=debortoli, dc=private', '(objectClass=posixGroup)')
        return self.conn.entries

    def getGroupsWithMembers(self):
        fq_groups = [result.entry_get_dn() for result in ldap.getGroups()]

        groups_with_members = {}
        for group in fq_groups:
            self.conn.search(group, '(objectclass=posixGroup)', attributes=['memberUid'])

            if 'memberUid' in self.conn.entries[0]:
                groups_with_members[group] = self.conn.entries[0]['memberUid'].values

        return groups_with_members

    def getMembersWithGroups(self):
        groups_with_members = self.getGroupsWithMembers()

        members_with_groups = {}
        for group, members in groups_with_members.iteritems():
            for member in members:
                if not member in members_with_groups:
                    members_with_groups[member] = []

                members_with_groups[member].append(group)

        return members_with_groups

    def addObjectClass(self, user, klass):
        self.conn.search('uid=%s, ou=People, dc=debortoli, dc=private' % user, '(objectclass=inetOrgPerson)', attributes=['objectClass'])

        assert len(self.conn.entries) > 0
        if not klass in self.conn.entries[0]['objectclass'].values:
            self.conn.modify('uid=%s, ou=People, dc=debortoli, dc=private' % user, {'objectClass': [(ldap3.MODIFY_ADD, [klass])]})
            return self.conn.result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=""" Syncs memberOf attribute onto users (inetOrgPerson) that are in posixGroups. Adds `inetUser` object class to the users if they don't already have it. """)
    parser.add_argument(
        '-D',
        '--user-dn',
        help='The user DN with correct permissions, such as Directory Manager.',
        default='cn=Directory Manager'
    )
    parser.add_argument(
        '-P',
        '--password-file',
        help='Password file that has the password in plaintext for the given user.',
        required=True
    )
    parser.add_argument(
        '-s',
        '--ldap-server',
        help='LDAP server hostname.',
        required=True
    )
    args = parser.parse_args()

    with open(args.password_file, 'r') as content_file:
        ldap_password = content_file.read().strip()

    ldap = Ldap(args.ldap_server, args.user_dn, ldap_password)

    members_with_groups = ldap.getMembersWithGroups()
    for member, groups in members_with_groups.iteritems():
        try:
            ldap.addObjectClass(member, 'inetUser')
        except AssertionError:
            print 'memberUid of %s does not have object class inetOrgPerson so not syncing.' % member
            continue

        ldap.conn.modify('uid=%s, ou=People, dc=debortoli, dc=private' % member, {'memberOf': [(ldap3.MODIFY_REPLACE, groups)]})
        print 'Synced memberOf for %s' % member
