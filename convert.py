import json
import os
from util import print_colored

class Convertor():
    def __init__(self,without_init=True):
        self.data = {}
        self.variable_type_to_moodel_field = {
            int: "models.IntegerField(blank=True,null=True)",
            str: "models.TextField(blank=True,null=True)",
            float: "models.DecimalField(blank=True,null=True,decimal_places=2,max_digits=10)",
            bool: "models.BooleanField(default=False)"
        }
        self.primary_keys = {}
        self.connections = {}
        self.generator_cluser = {
            'o2o' : {
                'direct' : self.get_direct_o2o_string,
                'indirect' : self.get_indirect_o2o_string
            },
            'o2m' : {
                'direct' : self.get_direct_o2m_string,
                'indirect': self.get_indirect_o2m_string
            },
            'm2m' : {
                'direct' : self.get_direct_m2m_string,
                'indirect' : self.get_indirect_m2m_string
            }
        }
        self.path = ''
        if without_init:
            if self.load_from_file():
                print_colored('Restored saved states from initData.json','green','b')
            else:
                print_colored("Couldn't restore because couldn't find initData.json. Do you want to overwrite (y|n)",'warning','b')
                choice = input()
                if choice not in ["y","yes"]:
                    print_colored("Aborting!","green","b")
                    exit()
                else:
                    print_colored("Overwriting!","red","b")
        
    def write_to_file(self):
        data = {
            'path' : self.path,
            'data' : self.data,
            'primary_keys' : self.primary_keys,
            'connections' : self.connections
        }
        with open('initData.json','w') as file:
            json.dump(data, file)

    def load_from_file(self):
        if os.path.exists('initData.json'):
            with open('initData.json', 'r') as file:
                dic = json.load(file)
                self.path = dic['path']
                self.data = dic['data']
                self.connections = dic['connections']
                self.primary_keys = dic['primary_keys']
            return True
        return False
    
    def code(self):
        print_colored('Starting writing backend', 'header', 'b')
        with open(self.path + '/models.py', 'w') as f:
            f.write(self.create_model_string())
        print_colored('Written successfully in models.py', 'green')
        with open(self.path + '/serializers.py', 'w') as f:
            f.write(self.create_serialiser_string())
        print_colored('Written successfully in serializers.py', 'green')
        with open(self.path + '/views.py', 'w') as f:
            f.write(self.create_views_string())
        print_colored('Written successfully in views.py', 'green')
        with open(self.path + '/urls.py', 'w') as f:
            f.write(self.create_urls_string())
        print_colored('Written successfully in urls.py', 'green')
        print_colored('Backend written successfully to all the files', 'green', 'b')
        backend_name = self.path.split('/')[0]
        print_colored(f'Starting migrations', 'blue')
        os.system(f'python3 {backend_name}/manage.py makemigrations')
        os.system(f'python3 {backend_name}/manage.py migrate')
        print_colored(f'Migration Successful!', 'green', 'b')
        print_colored("Created the following endpoint successfully","header","b")
        for class_name in self.data.keys():
            print_colored(f"GET localhost:8000/api/{class_name.lower()}","green")
            print_colored(f"POST localhost:8000/api/{class_name.lower()}/create","green")
            print_colored(f"GET PUT PATCH DELETE localhost:8000/api/{class_name.lower()}/:primary_key","green")
        
    def get_connection_string(self,con,to):
        if con == 'o2o':
            return f"models.OneToOneField('{to}',null=True,blank=True,on_delete=models.CASCADE)"
        elif con == 'o2m':
            return f"models.ForeignKey('{to}',null=True,blank=True,on_delete=models.CASCADE)"
        elif con == 'm2m':
            return f"models.ManyToManyField('{to}')"
        else:
            return "Unreachable"
        
    def ask_or_append(self,json_data,class_name,primary_key=None):
        class_name = class_name.title()
        if class_name in self.data.keys():
            print('Class with the same name already exists!!')
            choice = input('Do you want to overwrite it (y|n) : ').lower()
            if choice=='y' or choice=='yes':
                self.append(json_data,class_name)
            else:
                print('Aborting operation')
                return
            
        else:
            self.append(json_data,class_name)
        if primary_key:
            del self.data[class_name]['id']
            prev_val = self.data[class_name][primary_key]
            new_val = prev_val.split('(')[0]+'(primary_key=True,editable=False)'
            self.data[class_name][primary_key] = new_val
            self.primary_keys[class_name] = primary_key
        else:
            self.primary_keys[class_name] = "id"
        self.connections[class_name] = {
            'direct' : [],
            'indirect' : []
        }
        
    def create_connection(self,f,to,t):
        f = f.title()
        to = to.title()
        if t not in ['o2o','o2m','m2m']:
            print('Only possible connections are o2o o2m m2m')
            return 
        assert f in self.data.keys(),f'{f} not part of model'
        assert to in self.data.keys(),f'{to} not part of model'
        if to in [x['model'] for x in self.connections[f]['direct']] or \
            f in [x['model'] for x in self.connections[to]['indirect']]:
            choice = input('A connection already exists. Do you want to overwrite it (y|n) ')
            if choice.lower() in ["no","n"]:
                return
            else:
                #to be implemented
                pass
        self.connections[f]['direct'].append({'model':to,'type':t})
        self.connections[to]['indirect'].append({'model':f,'type':t})
        print_colored(f"Created {t} connection between {f} and {to}","green")
        print_colored(f"Exposed in {f} as field {f.lower()}_{to.lower()}","cyan")
        print_colored(f"Exposed in {to} as field {f.lower()}","cyan")
        
    def append(self,json_data,class_name):
        class_dic = {
            "id": "models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)",
            "created_on" : "models.DateTimeField(auto_now_add=True,editable=False)",
            "last_modified" : "models.DateTimeField(auto_now=True)"
        }
        for k,v in json_data.items():
            class_dic[str(k)] = self.variable_type_to_moodel_field[type(v)]
        self.data[class_name.title()] = class_dic
        
    def write_indirect_accessor_function(self,mod,typ):
        string_data = f"\tdef get_{mod.lower()}(self):\n"
        if typ=='o2o':
            string_data += '\t\ttry:\n'
            string_data += f'\t\t\treturn self.{mod.lower()}.{self.primary_keys[mod]}\n'
            string_data += '\t\texcept:\n'
            string_data += f'\t\t\treturn None\n\n'
            
        else:
            string_data += f'\t\t{mod.lower()}s = []\n'
            string_data += f'\t\tfor {mod.lower()} in self.{mod.lower()}_set.all():\n'
            string_data += f'\t\t\t{mod.lower()}s.append({mod.lower()}.{self.primary_keys[mod]})\n'
            string_data += f'\t\treturn {mod.lower()}s\n\n'
        return string_data

    def create_model_string(self):
        string_data = "from django.db import models\nimport uuid\n\n"
        for class_name,class_dic in self.data.items():
            string_data+=f'class {class_name.title()}(models.Model):\n'
            for k,v in class_dic.items():
                string_data+=f'\t{k} = {v}\n'
            for con in self.connections[class_name]['direct']:
                k,v = con['model'],con['type']
                string_data+=f'\t{class_name.lower()}_{k.lower()} = {self.get_connection_string(v,k)}\n'
            string_data+='\n'
            for con in self.connections[class_name]['indirect']:
                k,v = con['model'],con['type']
                string_data+=self.write_indirect_accessor_function(k,v)
        return string_data
            
    def create_serialiser_string(self):
        string_data = "from rest_framework import serializers\n"
        string_data += "from .models import *\n\n"
        for class_name in self.data.keys():
            string_data+=f'class {class_name.title()}Serializer(serializers.ModelSerializer):\n'
            string_data+=f'\tclass Meta:\n'
            string_data+=f'\t\tmodel = {class_name}\n'
            string_data+=f"\t\tfields = '__all__'\n\n"
        return string_data
    
    def get_indirect_m2m_string(self,f_mod,to_mod,indent=2):
        st = '\t'*indent
        string_data = ""
        to_mod_l = to_mod.lower()
        f_mod_l = f_mod.lower()
        string_data += f'{st}prev_{to_mod_l} = {f_mod_l}.get_{to_mod_l}()\n'
        string_data += f"{st}new_{to_mod_l} = data.get('{to_mod_l}',None)\n"
        string_data += f"{st}if new_{to_mod_l} is not None:\n"
        string_data += f"{st}\tfor val in prev_{to_mod_l}:\n"
        string_data += f"{st}\t\t{to_mod_l} = {to_mod}.objects.get({self.primary_keys[to_mod]}=val)\n"
        string_data += f"{st}\t\t{to_mod_l}.{to_mod_l}_{f_mod_l}.remove({f_mod_l})\n"
        string_data += f"{st}\tfor val in new_{to_mod_l}:\n"
        string_data += f"{st}\t\t{to_mod_l} = {to_mod}.objects.get({self.primary_keys[to_mod]}=val)\n"
        string_data += f"{st}\t\t{to_mod_l}.{to_mod_l}_{f_mod_l}.add({f_mod_l})\n"
        string_data += f"{st}\tdel data['{to_mod_l}']\n"
        return string_data
    
    def get_indirect_o2o_string(self,f_mod,to_mod,indent=2):
        st = '\t'*indent
        string_data = ""
        to_mod_l = to_mod.lower()
        f_mod_l = f_mod.lower()
        string_data += f'{st}prev_{to_mod_l} = {f_mod_l}.get_{to_mod_l}()\n'
        string_data += f"{st}new_{to_mod_l} = data.get('{to_mod_l}',None)\n"
        string_data += f"{st}if new_{to_mod_l} is not None:\n"
        string_data += f"{st}\tif prev_{to_mod_l} is not None:\n"
        string_data += f"{st}\t\t{to_mod_l} = {to_mod}.objects.get({self.primary_keys[to_mod]}=prev_{to_mod_l})\n"
        string_data += f"{st}\t\t{to_mod_l}.{to_mod_l}_{f_mod_l} = None\n"
        string_data += f"{st}\t\t{to_mod_l}.save()\n"
        string_data += f"{st}\t{to_mod_l} = {to_mod}.objects.get({self.primary_keys[to_mod]}=new_{to_mod_l})\n"
        string_data += f"{st}\t{to_mod_l}.{to_mod_l}_{f_mod_l} = {f_mod_l}\n"
        string_data += f"{st}\t{to_mod_l}.save()\n"
        string_data += f"{st}\tdel data['{to_mod_l}']\n"
        return string_data
    
    def get_indirect_o2m_string(self,f_mod,to_mod,indent=2):
        st = '\t'*indent
        string_data = ""
        to_mod_l = to_mod.lower()
        f_mod_l = f_mod.lower()
        string_data += f'{st}prev_{to_mod_l} = {f_mod_l}.get_{to_mod_l}()\n'
        string_data += f"{st}new_{to_mod_l} = data.get('{to_mod_l}',None)\n"
        string_data += f"{st}if new_{to_mod_l} is not None:\n"
        string_data += f"{st}\tfor val in prev_{to_mod_l}:\n"
        string_data += f"{st}\t\t{to_mod_l} = {to_mod}.objects.get({self.primary_keys[to_mod]}=val)\n"
        string_data += f"{st}\t\t{to_mod_l}.{to_mod_l}_{f_mod_l} = None\n"
        string_data += f"{st}\t\t{to_mod_l}.save()\n"
        string_data += f"{st}\tfor val in new_{to_mod_l}:\n"
        string_data += f"{st}\t\t{to_mod_l} = {to_mod}.objects.get({self.primary_keys[to_mod]}=val)\n"
        string_data += f"{st}\t\t{to_mod_l}.{to_mod_l}_{f_mod_l} = {f_mod_l}\n"
        string_data += f"{st}\t\t{to_mod_l}.save()\n"
        string_data += f"{st}\tdel data['{to_mod_l}']\n"
        return string_data
    
    def get_direct_m2m_string(self,f_mod,to_mod,indent=2):
        st = '\t'*indent
        string_data = ""
        to_mod_l = to_mod.lower()
        f_mod_l = f_mod.lower()
        to_mod_key = self.primary_keys[to_mod]
        string_data += f'{st}prev_{to_mod_l} = [x.{to_mod_key} for x in {f_mod_l}.{f_mod_l}_{to_mod_l}.all()]\n'
        string_data += f"{st}new_{to_mod_l} = data.get('{f_mod_l}_{to_mod_l}',None)\n"
        string_data += f"{st}if new_{to_mod_l} is not None:\n"
        string_data += f"{st}\tfor val in prev_{to_mod_l}:\n"
        string_data += f"{st}\t\t{to_mod_l} = {to_mod}.objects.get({self.primary_keys[to_mod]}=val)\n"
        string_data += f"{st}\t\t{f_mod_l}.{f_mod_l}_{to_mod_l}.remove({to_mod_l})\n"
        string_data += f"{st}\tfor val in new_{to_mod_l}:\n"
        string_data += f"{st}\t\t{to_mod_l} = {to_mod}.objects.get({self.primary_keys[to_mod]}=val)\n"
        string_data += f"{st}\t\t{f_mod_l}.{f_mod_l}_{to_mod_l}.add({to_mod_l})\n"
        string_data += f"{st}\tdel data['{f_mod_l}_{to_mod_l}']\n"
        return string_data
    
    def get_direct_o2o_string(self,f_mod,to_mod,indent=2):
        st = '\t'*indent
        string_data = ""
        to_mod_l = to_mod.lower()
        f_mod_l = f_mod.lower()
        string_data += f"{st}{f_mod_l}_{to_mod_l} = data.get('{f_mod_l}_{to_mod_l}',None)\n"
        string_data += f"{st}if {f_mod_l}_{to_mod_l} is not None:\n"
        string_data += f"{st}\t{to_mod_l} = {to_mod}.objects.get({self.primary_keys[to_mod]}={f_mod_l}_{to_mod_l})\n"
        string_data += f"{st}\t{f_mod_l}.{f_mod_l}_{to_mod_l} = {to_mod_l}\n"
        string_data += f"{st}\t{f_mod_l}.save()\n"
        string_data += f"{st}\tdel data['{f_mod_l}_{to_mod_l}']\n"
        return string_data
    
    def get_direct_o2m_string(self,f_mod,to_mod,indent=2):
        st = '\t'*indent
        string_data = ""
        to_mod_l = to_mod.lower()
        f_mod_l = f_mod.lower()
        string_data += f"{st}val = data.get('{f_mod_l}_{to_mod_l}',None)\n"
        string_data += f"{st}if val is not None:\n"
        string_data += f"{st}\t{to_mod_l} = {to_mod}.objects.get({self.primary_keys[to_mod]}=val)\n"
        string_data += f"{st}\t{f_mod_l}.{f_mod_l}_{to_mod_l} = {to_mod_l}\n"
        string_data += f"{st}\t{f_mod_l}.save()\n"
        string_data += f"{st}\tdel data['{f_mod_l}_{to_mod_l}']\n"
        return string_data
    
    def generate_static_add_connection(self,class_name):
        string_data = '\t@staticmethod\n'
        string_data += f'\tdef add_connection({class_name.lower()},data):\n'
        for con in self.connections[class_name]['direct']:
            con_type,to_mod = con['type'],con['model']
            string_data += self.generator_cluser[con_type]['direct'](class_name,to_mod)
            
        for con in self.connections[class_name]['indirect']:
            con_type,to_mod = con['type'],con['model']
            string_data += self.generator_cluser[con_type]['indirect'](class_name,to_mod)
        string_data += '\t\treturn data\n\n'
        return string_data
        
    def generate_connection_addition_to_get(self,class_name):
        string_data = ""
        for con in self.connections[class_name]['indirect']:
            to_mod = con['model'].lower()
            string_data += f"\t\tdata['{to_mod}'] = {class_name.lower()}.get_{to_mod}()\n"
        return string_data
            
    def check_connection(self,class_name):
        indirect_con = len(self.connections[class_name]['indirect'])
        direct_con = len(self.connections[class_name]['direct'])
        num_con = indirect_con + direct_con
        return num_con > 0
    
    def create_views_string(self):
        
        def check_existence(class_name):
            string_data = f"\t\ttry:\n"
            string_data += f"\t\t\t{class_name.lower()} = {class_name}.objects.get({self.primary_keys[class_name]}=pk)\n"
            string_data += f"\t\texcept:\n"
            string_data += f"\t\t\treturn Response({{'detail':'{class_name} does not exist.'}},status=status.HTTP_400_BAD_REQUEST)\n"
            return string_data
        
        def add_put_or_patch(class_name,partial):
            isPartial = "True" if partial else "False"
            fun_name = "patch" if partial else "put"
            string_data = f"\tdef {fun_name}(self,request,pk):\n"
            string_data += check_existence(class_name)
            string_data += "\t\tdata = request.data\n"
            if self.check_connection(class_name):
                string_data += f"\t\tdata = self.add_connection({class_name.lower()},data)\n"
            string_data += f"\t\tserialized = {class_name}Serializer({class_name.lower()},data=data,partial={isPartial})\n"
            string_data += f"\t\tif serialized.is_valid():\n"
            string_data += f"\t\t\tserialized.save()\n"
            string_data += f"\t\t\treturn self.get(request=request,pk=pk)\n"
            string_data += f"\t\treturn Response({{'detail':'Some error occured check field names'}},status=status.HTTP_400_BAD_REQUEST)\n\n"
            return string_data
        
        string_data = "from rest_framework.decorators import api_view\n"
        string_data += "from rest_framework.views import APIView\n"
        string_data += "from rest_framework.response import Response\n"
        string_data += "from rest_framework import status\n"
        string_data += "from .models import *\n"
        string_data += "from .serializers import *\n\n"
        for class_name in self.data.keys():
            string_data += "@api_view(['GET'])\n"
            string_data += f"def get_all_{class_name.lower()}(request):\n"
            string_data += f"\t{class_name.lower()}s = {class_name}.objects.all()\n"
            string_data += f"\tserialized = {class_name}Serializer({class_name.lower()}s,many=True)\n"
            string_data += f"\treturn Response(serialized.data,status=status.HTTP_200_OK)\n\n"
            string_data += "@api_view(['POST'])\n"
            string_data += f"def create_{class_name.lower()}(request):\n"
            string_data += "\tdata = request.data\n"
            if self.primary_keys[class_name]=="id":
                string_data += f"\t{class_name.lower()} = {class_name}.objects.create()\n"
            else:
                string_data += "\ttry:\n"
                string_data += f"\t\t{class_name.lower()} = {class_name}.objects.create({self.primary_keys[class_name]}=data['{self.primary_keys[class_name]}'])\n"
                string_data += "\texcept:\n"
                string_data += f"\t\treturn Response({{'detail':'{self.primary_keys[class_name]} should be prvided to create {class_name}'}},status=status.HTTP_400_BAD_REQUEST)\n"
            if self.check_connection(class_name):
                string_data += f"\tdata = {class_name}APIView.add_connection({class_name.lower()},data)\n"
            string_data += f"\tserialized = {class_name}Serializer({class_name.lower()},data=data,partial=True)\n"
            string_data += f"\tif serialized.is_valid():\n"
            string_data += f"\t\tserialized.save()\n"
            string_data += f"\t\treturn Response(serialized.data,status=status.HTTP_200_OK)\n\n"
            string_data += f"\treturn Response({{'detail':'Some error occured check field names'}},status=status.HTTP_400_BAD_REQUEST)\n\n"
            string_data += f"class {class_name}APIView(APIView):\n"
            string_data += f"\tdef get(self,request,pk):\n"
            string_data += check_existence(class_name)
            string_data += f"\t\tserialized = {class_name}Serializer({class_name.lower()},many=False)\n"
            string_data += f"\t\tdata = serialized.data\n"
            string_data += self.generate_connection_addition_to_get(class_name)
            string_data += f"\t\treturn Response(data,status=status.HTTP_200_OK)\n\n"
            if self.check_connection(class_name):
                string_data += self.generate_static_add_connection(class_name)
            string_data += add_put_or_patch(class_name,False)
            string_data += add_put_or_patch(class_name,True)
            string_data += "\tdef delete(self,request,pk):\n"
            string_data += check_existence(class_name)
            string_data += "\t\ttry:\n"
            string_data += f"\t\t\t{class_name.lower()}.delete()\n"
            string_data += "\t\t\treturn Response({'Message':'Deleted Successfully'},status=status.HTTP_200_OK)\n"
            string_data += "\t\texcept:\n"
            string_data += "\t\t\treturn Response({'detail':'Some error occured while deleting'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)\n\n"
        return string_data
    
    def create_urls_string(self):
        string_data = "from django.urls import path\nfrom . import views\n\n"
        string_data += "urlpatterns = [\n"
        for class_name in self.data.keys():
            string_data += f"\tpath('{class_name.lower()}',views.get_all_{class_name.lower()}),\n"
            string_data += f"\tpath('{class_name.lower()}/create',views.create_{class_name.lower()}),\n"
            string_data += f"\tpath('{class_name.lower()}/<slug:pk>',views.{class_name}APIView.as_view()),\n"
        string_data += ']'
        return string_data