import base64
import io
import os
import shutil
import subprocess
import zipfile
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
import json
import datetime
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
import psutil
from django.middleware.csrf import get_token
from django.contrib.auth import login, authenticate, get_user_model

from users.models import CustomUser as User
from .serializers import UserSerializer


class UserLogin(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
                login(request, user)
                serialized_data = UserSerializer(user,many=False)
                return JsonResponse({'success': 'Login successful','user':serialized_data.data},status=status.HTTP_200_OK)
        else:
            return JsonResponse({'error': 'Login failed'},status=status.HTTP_401_UNAUTHORIZED)


class GetCSRFToken(APIView):
    permission_classes = (AllowAny,)
    def get(self, request, format=None):
        csrf_token = get_token(request)
        return Response({'success':'CSRF cookie set', 'csrf-token':csrf_token})


class ClassMyProfile(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        elif self.request.method == 'GET':
            return [IsAuthenticated()]
        else:
            return [IsAuthenticated()]


    def get(self, request):
        try:
            id = request.user.id

            try:

                user = get_object_or_404(User, pk=id)
                serialized_data = UserSerializer(user, many=False)

                return Response({'success':serialized_data.data})
            except Exception as e:
                return Response({'error':str(e)})
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductionBackupManage(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        try:
            folder_path = settings.BACKUP_FRONTEND_FILE_PATH # Replace this with the path to your folder
            folders_info = []
            for folder_name in os.listdir(folder_path):
                folder_full_path = os.path.join(folder_path, folder_name)
                if os.path.isdir(folder_full_path):
                    created_time = datetime.datetime.fromtimestamp(os.path.getctime(folder_full_path)).strftime('%Y-%m-%d %H:%M:%S')
                    folders_info.append({'folder_name': folder_name, 'created_date': created_time})

            return Response({'success':'Successsfuly fetched backups','backups': folders_info})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            cmd = request.data.get('cmd')
            if cmd == 'restore':
                folder = request.data.get('folder')

                if folder:
                    source_folder = settings.BACKUP_FRONTEND_FILE_PATH + '/' + folder  # Replace with source folder path
                    destination_folder = settings.FRONTEND_FILE_PATH  # Replace with destination folder path

                    # Check if source and destination folders exist
                    if not os.path.exists(source_folder) or not os.path.exists(destination_folder):
                        return Response({'error': 'Source or destination folder does not exist'}, status=status.HTTP_404_NOT_FOUND)

                    # Copy source folder to destination folder (including subfolders)
                    shutil.copytree(source_folder, destination_folder,dirs_exist_ok=True)

                    return Response({'success': 'Successfully restored'})
                else:
                    return Response({'error': 'Folder not provided'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Unknown command'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductionFrontEndUpdater(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        try:

            cmd = request.data.get('cmd')

            if cmd != None:
                if cmd == 'restart_nginx':
                    password = settings.UBUNTU_PASS
                    # Validate password or perform any necessary checks

                    # Construct the command to restart Nginx sudo systemctl restart nginx
                    command = ['sudo', '-S', 'systemctl', 'restart', 'nginx']

                    # Use subprocess to execute the command
                    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    output, error = process.communicate(input=password + '\n')  # Provide the password to sudo

                    if process.returncode == 0:
                        return Response({'success': 'Nginx restarted successfully'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'error': f'Error restarting Nginx. Exit code: {process.returncode}', 'output': output, 'error_output': error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                # sudo certbot --nginx -d pylessons.me -d www.pylessons.me
                if cmd == 'generate_cert':
                    password = settings.UBUNTU_PASS
                    # Validate password or perform any necessary checks


                    command = ['sudo', '-S','certbot','--nginx','-d', settings.NAME_OF_NGINX_CONFIG_FILE]

                    # Use subprocess to execute the command
                    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    output, error = process.communicate(input=password + '\n')  # Provide the password to sudo

                    if process.returncode == 0:
                        return Response({'success': 'Successfully executed.'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'error': f'Error execution. Exit msg: {output}. Output Err: {error}', 'output': output, 'error_output': error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                if cmd == 'renew_cert':
                    password = settings.UBUNTU_PASS
                    # Validate password or perform any necessary checks


                    command = ['sudo', '-S','certbot','renew ']

                    # Use subprocess to execute the command
                    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    output, error = process.communicate(input=password + '\n')  # Provide the password to sudo

                    if process.returncode == 0:
                        return Response({'success': f'Successfully executed. {output}'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'error': f'Error execution. Exit msg: {output}. Output Err: {error}', 'output': output, 'error_output': error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                else:
                    return Response({'error':'Unknown command'})

            # Get the base64-encoded zip file from the request
            file_data = request.data.get('data')
            if not file_data:
                return Response({'error': 'No data provided'}, status=status.HTTP_400_BAD_REQUEST)

            # Decode the base64 string
            zip_data = base64.b64decode(file_data)

            # Specify the folder where you want to extract the files
            extract_folder = settings.FRONTEND_FILE_PATH
            backup_folder_base = settings.BACKUP_FRONTEND_FILE_PATH

            # Find the latest existing backup folder
            existing_backups = [d for d in os.listdir(backup_folder_base) if d.startswith('backup')]
            existing_backups.sort(key=lambda x: int(x.replace('backup', '')) if x.replace('backup', '').isdigit() else -1, reverse=True)
            latest_backup = existing_backups[0] if existing_backups else None

            # Increment the backup folder name
            if latest_backup:
                backup_number = int(latest_backup.replace('backup', '')) + 1
            else:
                backup_number = 1

            # Create a new backup folder
            backup_folder = os.path.join(backup_folder_base, f'backup{backup_number}')
            os.makedirs(backup_folder, exist_ok=True)

            # Move all files into the new backup folder
            for item in os.listdir(extract_folder):
                item_path = os.path.join(extract_folder, item)
                shutil.move(item_path, os.path.join(backup_folder, item))

            # Create a BytesIO object to read the zip data
            zip_io = io.BytesIO(zip_data)

            # Extract the zip file to the specified folder
            with zipfile.ZipFile(zip_io, 'r') as zip_ref:
                zip_ref.extractall(extract_folder)

            return Response({'success': 'Files extracted, and existing files backed up successfully'}, status=status.HTTP_200_OK)

        except zipfile.BadZipFile:
            return Response({'error': 'Invalid zip file'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductionServerStatus(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        try:
            # Gathering system information

            ram = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # Constructing the response
           # Gathering system information
            cpu_count_physical = psutil.cpu_count(logical=False)
            cpu_count_logical = psutil.cpu_count(logical=True)
            cpu_percent = psutil.cpu_percent(interval=1)

            # Calculate total and available CPU resources
            total_cores = cpu_count_physical + cpu_count_logical
            used_cores = total_cores * (cpu_percent / 100)  # Calculate the number of used cores based on CPU percentage
            free_cores = total_cores - used_cores

            # print("Total Used Cores:", used_cores)
            # print("Total Free Cores:", free_cores)

            # Constructing the response
            server_status = {
                'success': 'Successfully fetched',
                'cpu': {
                    'Used Cores (L+P)': used_cores,
                    'Available': free_cores,

                    'percent_usage': cpu_percent
                },
                'ram': {
                    'Used (GB)': ram.used  / (1024 ** 3),
                    'Available (GB)': ram.available  / (1024 ** 3),
                    'percent_usage': ram.percent
                },
                'disk': {
                    'Used (GB)': disk.used  / (1024 ** 3),
                    'Available (GB)': disk.free  / (1024 ** 3),
                    # 'free': disk.free  / (1024 ** 3),
                    'percent_usage': disk.percent
                }
            }


            return Response(server_status)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UFWManager(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
            type = request.data.get('type')
            if type == 'status':
                password = settings.UBUNTU_PASS
                # First command: 'sudo -S ufw status'
                ufw_command = ['sudo', '-S', 'ufw', 'status', 'numbered']
                # Second command: 'jc --ufw'
                jc_command = ['jc', '--ufw']

                # Run the first command and capture its output
                ufw_process = subprocess.run(ufw_command, input=password, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if ufw_process.returncode != 0:
                    print(f"Error executing ufw status: {ufw_process.stderr}")
                    exit(1)

                # Run the second command using the output of the first command as input
                jc_process = subprocess.run(jc_command, input=ufw_process.stdout, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if jc_process.returncode != 0:
                    print(f"Error executing jc --ufw: {jc_process.stderr}")
                    exit(1)

                # Get the final output
                output = jc_process.stdout
                json_result = json.loads(output)
                if jc_process.returncode == 0:
                    return Response({'success': f'Successfully executed.', 'data':json_result}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': f'Error execution. Exit msg: {output}. Output Err: {error}', 'output': output, 'error_output': error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


            elif type == 'add':
                password = settings.UBUNTU_PASS
                new_ip = request.data.get('ip')
                port = request.data.get('port')
                if (new_ip==None) or (port ==None):
                    return Response({'error':'Missing fields'}, status=status.HTTP_400_BAD_REQUEST)

                command = ['sudo', '-S', 'ufw', 'allow', 'from', new_ip, 'proto', 'tcp', 'to', 'any', 'port', port]

                # Use subprocess to execute the command
                process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,start_new_session=True)
                output, error = process.communicate(input=password + '\n')  # Provide the password to sudo

                if process.returncode == 0:
                    return Response({'success': f'Successfully executed. {output}'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': f'Error execution. Exit msg: {output}. Output Err: {error}', 'output': output, 'error_output': error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            elif type == 'remove':
                pass
            elif type == 'reload':
                pass
            elif type == 'activate':
                password = settings.UBUNTU_PASS
                command = ['sudo', '-S', 'ufw', 'enable']

                # Use subprocess to execute the command
                process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,start_new_session=True)
                output, error = process.communicate(input=password + '\n')  # Provide the password to sudo

                if process.returncode == 0:
                    return Response({'success': f'Successfully executed. {output}'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': f'Error execution. Exit msg: {output}. Output Err: {error}', 'output': output, 'error_output': error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            elif type == 'deactivate':
                password = settings.UBUNTU_PASS
                command = ['sudo', '-S', 'ufw', 'disable']

                # Use subprocess to execute the command
                process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,start_new_session=True)
                output, error = process.communicate(input=password + '\n')  # Provide the password to sudo

                if process.returncode == 0:
                    return Response({'success': f'Successfully executed. {output}'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': f'Error execution. Exit msg: {output}. Output Err: {error}', 'output': output, 'error_output': error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({'error':'Unknown Type'}, status =status.HTTP_500_INTERNAL_SERVER_ERROR)
