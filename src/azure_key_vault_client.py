import os
import cmd
import datetime

'''
   从azure 的key vault获取密钥方法(https://docs.microsoft.com/zh-cn/azure/key-vault/secrets/quick-create-python?tabs=cmd)

   创建client
   1、利用azure client 登录，获取凭证(开发者模式)
      a、安装azure client(https://docs.microsoft.com/zh-cn/cli/azure/install-azure-cli)
         Ubuntu安装: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
      b、登录到azure(az login/az login -u <USER_NAME> -p <USER_PASSWORD>), 登录账户需要azure管理员创建并设置合适的策略 
      c、利用DefaultAzureCredential在程序中获取登录凭证
      d、退出登录，清除凭证az logout

   2、在azure云服务器(虚拟机)上运行程序(适合上线时候用，相对安全)
      a、在azure云上部署虚拟机并认证该服务器，azure管理员操作
      b、利用DefaultAzureCredential在程序中获取登录凭证

   3、利用环境变量设置相应的ID(开发者模式或上线时用)
      a、设置环境变量(参照(Service principal with secret)：https://azuresdkdocs.blob.core.windows.net/$web/python/azure-identity/1.4.0/azure.identity.html#azure.identity.EnvironmentCredential)
      b、利用DefaultAzureCredential在程序中获取登录凭证

   获取secret过程：
   1、SecretClient初始化，获取client
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=uri, credential=credential)
      
   2、获取指定vault_name中的key_name的值key_value
        client.get_secret/client.set_secret
      
   ****************************************************************************************
    **DefaultAzureCredential
        DefaultAzureCredential is appropriate for most applications which will run in the Azure Cloud because it combines common production credentials with development credentials. DefaultAzureCredential attempts to authenticate via the following mechanisms in this order, stopping when one succeeds:
        Environment - DefaultAzureCredential will read account information specified via environment variables and use it to authenticate.
        Managed Identity - if the application is deployed to an Azure host with Managed Identity enabled, DefaultAzureCredential will authenticate with it.
        Visual Studio Code - if a user has signed in to the Visual Studio Code Azure Account extension, DefaultAzureCredential will authenticate as that user.
        Azure CLI - If a user has signed in via the Azure CLI az login command, DefaultAzureCredential will authenticate as that user.
        Interactive - If enabled, DefaultAzureCredential will interactively authenticate a user via the current system's default browser.'

    可指定类型：
        DefaultAzureCredential,
        EnvironmentCredential,
        InteractiveBrowserCredential

    参照以下Python代码实现：
'''


from azure.keyvault.secrets import SecretClient
from azure.identity import (
        DefaultAzureCredential,
        EnvironmentCredential,
        InteractiveBrowserCredential
        )

'''
初始化环境：参照创建client部分说明
测试本代码时本地环境：
   os: ubuntu 16.84 推荐 ubuntu 18.04 或更高（默认安装了python 3.6+）
   Python版本：3.6.9
   azure cli: 2.16.0
   安装了azure-identity
   安装了azure-keyvault-secrets

执行以下操作，你或许就可以按照 方法1 或 方法2 执行此代码：
   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
   pip install azure-identity
   pip install azure-keyvault-secrets
   export AZURE_CLIENT_ID = "80f16cbd-e549-4c93-9e7b-22a91c8615d4"
   export AZURE_TENANT_ID = "d99eee11-8587-4c34-9201-38d5247df9c9"
   export AZURE_CLIENT_SECRET = "sUN0g~V9o81.M5UP1tJHKRMgxS_ru7g~O~"

   $> python3 kv_secrets_env.py



方法1、方法2都可用

方法1：linux下设置环境变量（以下值可能已过期，需要从azure管理员处获取）
   #设置application id
   export AZURE_CLIENT_ID = "80f16cbd-e549-4c93-9e7b-22a91c8615d4"
   #设置目录(租户)ID
   export AZURE_TENANT_ID = "d99eee11-8587-4c34-9201-38d5247df9c9"
   #设置application下的服务主题密钥（从管理员处获取)
   export AZURE_CLIENT_SECRET = "sUN0g~V9o81.M5UP1tJHKRMgxS_ru7g~O~"

方法2：azure cli 登录
   请更azure管理员联系，分配账户并设置访问key vault的访问策略


'''

from enum import (
        Enum,
        auto
        )

class enumbase(Enum):
    @property
    def info(self):
        return f"{self.name}:{self.value}"

    @property
    def env(self):
        try:
            return os.getenv(self.name)
        except Exception as e:
            pass
        return None

    @env.setter
    def env(self, value):
        os.environ[self.name] = value

    def env_del():
        if self.env:
            del os.environ[self.name]

class autouppername(enumbase):
    def _generate_next_value_(name, start, count, last_values):
        return name.upper()

class azure_environ_name(autouppername):
    AZURE_CLIENT_ID     = auto()
    AZURE_TENANT_ID     = auto()
    AZURE_CLIENT_SECRET = auto()

def get_key_value_uri(vault_name):
    return f"https://{vault_name}.vault.azure.net"

def get_client(uri):
    credential = DefaultAzureCredential()
    return SecretClient(vault_url=uri, credential=credential)

'''
从vault_name 中获取key_name存储的密钥
'''
def get_secret(vault_name, key_name):
    client = get_client(get_key_value_uri(vault_name))
    return client.get_secret(key_name).value

'''
设置vault_name 中key_name存储的密钥
'''
def set_secret(vault_name, key_name, key_value):
    client = get_client(get_key_value_uri(vault_name))
    return client.set_secret(key_name, key_value)

'''
删除vault_name 中key_name及值
'''
def del_secret(vault_name, key_name):
    client = get_client(get_key_value_uri(vault_name))
    poller = client.begin_delete_secret(key_name)
    deleted_secret = poller.result()

    name = deleted_secret.name

    # if the vault has soft-delete enabled, the secret's, deleted_date
    # scheduled purge date and recovery id are set
    # if you want to block until secret is deleted server-side, call wait() on the poller
    poller.wait()
    return name
    
'''
显示vault_name 中可用key
'''
def show_secrets(vault_name):
    client = get_client(get_key_value_uri(vault_name))
    return [s.name for s in client.list_properties_of_secrets()]
