#!/usr/bin/env python

import re
import sys
import time

from selenium import webdriver
from optparse import OptionParser
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

class MetaMeetupInactivitykicker(type):

    def __new__(meta,name,bases,dct):
        return super(MetaMeetupInactivitykicker, meta).__new__(meta, name, bases, dct)

    def __init__(cls,name,bases,dct):
        if not hasattr(cls,'count'):
            cls.count = 0
        if not hasattr(cls,'member_list'):
            cls.member_list = {}
        if not hasattr(cls,'member_name'):
            cls.site_name = None
        if not hasattr(cls,'driver'):
            user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0'
            profile    = webdriver.FirefoxProfile()
            profile.set_preference("general.useragent.override", user_agent)
            cls.driver = webdriver.Firefox(profile)


class MeetupInactivitykicker(object):

    __metaclass__ = MetaMeetupInactivitykicker

    def __init__(self,config_dict={}):
        self.email                = config_dict['email'] 
        self.dry_run              = config_dict['dry_run']
        self.password             = config_dict['password']
        self.group_name           = config_dict['group_name']
        self.removal_message      = config_dict['removal_message']
        self.warning_message      = config_dict['warning_message']
        self.send_removal_message = config_dict['send_removal_message']
        self.send_warning_message = config_dict['send_warning_message']

    def back(self):
        try:
            MeetupInactivitykicker.driver.back()
        except:
            MeetupInactivitykicker.driver.execute_script("window.history.go(-1)")
            pass

    def populate_member_dict(self, elements):
        for element in elements:
            href = element.get_attribute("href")
            member = re.search('https://www.meetup.com/'
                + str(MeetupInactivitykicker.site_name)
                + 'members/(\d+)/profile/.*', href, re.M | re.I)
            if member is not None:
                MeetupInactivitykicker.member_list[member.group(1)] = member.group()

    def navigate_to_members_page(self, elements):
        for element in elements:
            try:
                href = element.get_attribute("href")
                res  = re.findall('https://www.meetup.com/*'
                    + str(self.group_name)
                    + '.*', href, re.I | re.M)
                if res:
                    MeetupInactivitykicker.count += 1
                    if MeetupInactivitykicker.count > 1:
                        print("The group name you've provided is to vage")
                        sys.exit(1)
                    MeetupInactivitykicker.count += 1
                MeetupInactivitykicker.driver.get(str(res[0])+'/members')
                MeetupInactivitykicker.site_name = re.sub('https://www.meetup.com/', '', res[0])
            except Exception as exception:
                pass

    def remove_member(self):
        MeetupInactivitykicker.driver.find_element_by_css_selector("svg.svg.svg--overflow.svg-icon.valign--middle").click()
        MeetupInactivitykicker.driver.find_element_by_class_name('member-actions-menuItem-remove_member.dropdownMenu-item.display--flex.span--100').click()
        if self.send_removal_message:
            MeetupInactivitykicker.driver.find_element_by_css_selector('textarea#removeMemberModalTextarea').send_keys(self.removal_message)
        if not self.dry_run:
            print('Removing '
                + str(MeetupInactivitykicker.member_name)
                + ' from group!')
            MeetupInactivitykicker.driver.find_element_by_xpath("//span[text()='Remove member']").click()

    def warn_member(self):
        MeetupInactivitykicker.driver.find_element_by_css_selector("a.text--small.messageButton").click()
        if self.send_warning_message:
            MeetupInactivitykicker.driver.find_element_by_css_selector('textarea#messaging-new-convo.composeBox-textArea').send_keys(self.warning_message)
        if not self.dry_run:
            print('Sending '
                + str(MeetupInactivitykicker.member_name)
                + ' a warning message!')
            MeetupInactivitykicker.driver.find_element_by_class_name('composeBox-sendButton.j-messageSend.messagingButton').send_keys(Keys.RETURN)
        self.back()

    def active(self, status):
        try:
            result = MeetupInactivitykicker.driver.find_element_by_xpath("//span[text()=\""
                + str(status)
                + "\"]").text
            if 'no' in result:
                regex = re.search('\d+ no', result, re.M | re.I).group()
            if 'yes' in result:
                regex = re.search('0 yes', result, re.M | re.I).group()
            if 'None' in result:
                regex = re.search('None', result, re.M | re.I).group()
            return True
        except:
            return False

    def login(self):
        MeetupInactivitykicker.driver.get("https://secure.meetup.com/login")
        uname = MeetupInactivitykicker.driver.find_element_by_name("email")
        uname.send_keys(self.email)
        pword = MeetupInactivitykicker.driver.find_element_by_name("password")
        pword.send_keys(self.password,Keys.RETURN)
        time.sleep(5)

    def main(self):
        try:
            MeetupInactivitykicker.driver.find_element_by_class_name('simple-view-selector-anc').click()
        except NoSuchElementException as noSuchElementException:
            print('Exception NoSuchElementException => '+str(noSuchElementException))
            sys.exit(1)
        self.navigate_to_members_page(MeetupInactivitykicker.driver.find_elements_by_xpath("//a[@href]"))
        self.populate_member_dict(MeetupInactivitykicker.driver.find_elements_by_xpath("//a[@href]"))
        for idno, member in sorted(MeetupInactivitykicker.member_list.items()):
            MeetupInactivitykicker.driver.get(str(member))
            del MeetupInactivitykicker.member_list[idno]
            try:
                if self.active('None') or self.active('yes'):
                    member_name_regex = "//div[@class='flex-item']/p[@class='text--big text--bold']"
                    MeetupInactivitykicker.member_name = MeetupInactivitykicker.driver.find_element_by_xpath(member_name_regex).text
                    self.remove_member()
                    #self.warn_member()
                self.back()
            except :
                pass

if __name__ == '__main__':

    removal_message = 'You have been inactive in this group and are being removed by automated software.'
    warning_message = 'You have been inactive in this group and will be removed if the inactivity continues.'

    parser = OptionParser()
    parser.add_option('-e', '--email',
        dest='email', default='example@email.com',
        help='This is your MeetUp E-mail.')
    parser.add_option('-p', '--password',
        dest='password', default='password',
        help='This is your MeetUp login password.')
    parser.add_option('-k', '--keyword',
        dest='group_name',
        help='This is the group name you would like to search on Meetup.com.')
    parser.add_option('-R', '--retry',
        dest='retry', action="store_true", default=False,
        help='This options ensures that this program will try again if it cannot login.')
    parser.add_option('-t', '--timeout',
        dest='timeout',type='int',
        help='This options sets the time in between each retry.')
    parser.add_option('-d', '--dry-run',
        dest='dry_run',action='store_true', default=False,
        help='This options runs the script without deleting members.')
    parser.add_option('-S', '--send-removal-message',
        dest='send_removal_message', action='store_true', default=False,
        help='This options sends the default removal message if a custom message isnt passed.')
    parser.add_option('-s', '--send-warning-message',
        dest='send_warning_message', action='store_true', default=False,
        help='This options sends the default warning message if a custom message isnt passed.')
    parser.add_option('-r', '--removal-message',
        dest='removal_message', default=removal_message,
        help='This options sends a custom removal message.')
    parser.add_option('-w', '--warning-message',
        dest='warning_message', default=warning_message,
        help='This options sends a custom warning message.')
    (options, args) = parser.parse_args()

    config_dict = {
      'retry'                : options.retry,
      'email'                : options.email,
      'timeout'              : options.timeout,
      'dry_run'              : options.dry_run,
      'password'             : options.password,
      'group_name'           : options.group_name,
      'removal_message'      : options.removal_message,
      'warning_message'      : options.warning_message,
      'send_removal_message' : options.send_removal_message,
      'send_warning_message' : options.send_warning_message,
    }

    meetupInactivityKicker = MeetupInactivitykicker(config_dict)
    meetupInactivityKicker.login()
    meetupInactivityKicker.main()
