#!/usr/bin/env python

import re
import sys
import time

from selenium import webdriver
from optparse import OptionParser
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

class MeetupInactivitykicker(object):

    def __init__(self,config_dict={}):
        self.site_name  = None
        self.email      = config_dict['email'] 
        self.password   = config_dict['password']
        self.group_name = config_dict['group_name']
        user_agent      = 'Mozilla/5.0 (X11; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0'
        profile         = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", user_agent)
        self.driver     = webdriver.Firefox(profile)
        self.driver.get("https://secure.meetup.com/login")

    def remove_member(self, member):
        self.driver.find_element_by_css_selector("svg.svg.svg--overflow.svg-icon.valign--middle").click()
        self.driver.find_element_by_class_name('member-actions-menuItem-remove_member.dropdownMenu-item.display--flex.span--100').click()

        message = 'You have been inactive in this group and are being removed by automated software.'
        text_box = self.driver.find_element_by_css_selector('textarea#removeMemberModalTextarea').send_keys(message)
        self.driver.find_elements_by_xpath("//span[contains(text(), 'Remove member')]").click()

    def active(self, status):
        try:
            status = self.driver.find_element_by_xpath("//span[contains(text(),"+str(status)+")]").text
            if 'no' in status:
                regex = re.search('\d+', status, re.M | re.I).group()
            if 'yes' in status:
                regex = re.search('0', status, re.M | re.I).group()
            if 'None' in status:
                regex = re.search('None', status, re.M | re.I).group()
            return True
        except:
            return False

    def login(self):
        uname = self.driver.find_element_by_name("email")
        uname.send_keys(self.email)
        pword = self.driver.find_element_by_name("password")
        pword.send_keys(self.password,Keys.RETURN)
        time.sleep(5)

    def main(self):
        count = 0
        try:
            self.driver.find_element_by_class_name('simple-view-selector-anc').click()
        except NoSuchElementException as noSuchElementException:
            print('Exception NoSuchElementException => '+str(noSuchElementException))
            sys.exit(1)
        elems = self.driver.find_elements_by_xpath("//a[@href]")
        for elem in elems:
            try:
                href = elem.get_attribute("href")
                res  = re.findall('https://www.meetup.com/*'+str(self.group_name)+'.*', href, re.I | re.M)
                if res:
                    count += 1
                    if count > 1:
                        print("The group name you've provided is to vage")
                        sys.exit(1)
                    count += 1
                self.driver.get(str(res[0])+'/members')
                self.site_name = re.sub('https://www.meetup.com/', '', res[0])
            except Exception as exception:
                pass
        member_name = None
        member_list = {}
        elems = self.driver.find_elements_by_xpath("//a[@href]")
        for elem in elems:
            href = elem.get_attribute("href")
            member = re.search('https://www.meetup.com/'+str(self.site_name)+'members/(\d+)/profile/.*', href, re.M | re.I)
            if member is not None:
                member_list[member.group(1)] = member.group()
                #member_name = self.driver.find_element_by_css_selector(".text--big, .text--display3").text
                #print member_name
        for idno, member in sorted(member_list.items()):
            self.driver.get(str(member))
            del member_list[idno]
            try:
                #none = self.driver.find_element_by_xpath("//span[contains(text(), 'None')]").text
                if self.active('None') or self.active('yes'):
                    #remove from group
                    print('Removing '+str(idno)+' from group!')
                    self.remove_member(member)
                try:
                    self.driver.back()
                except:
                    self.driver.execute_script("window.history.go(-1)")
                    pass
            except :
                pass

if __name__ == '__main__':

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
    parser.add_option('-r', '--retry',
        dest='retry', action="store_true", default=False,
        help='This options ensures that this program will try again if it cannot login.')
    parser.add_option('-t', '--timeout',
        dest='timeout',type='int',
        help='This options sets the time in between each retry.')
    (options, args) = parser.parse_args()

    config_dict = {
      'retry'      : options.retry,
      'email'      : options.email,
      'timeout'    : options.timeout,
      'password'   : options.password,
      'group_name' : options.group_name
    }

    meetupInactivityKicker = MeetupInactivitykicker(config_dict)
    meetupInactivityKicker.login()
    meetupInactivityKicker.main()