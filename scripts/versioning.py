#!/usr/bin/env python3
import re
import subprocess
import json
from datetime import datetime
import os

def get_current_version():
    """Obtém a versão atual do package.json ou version.txt"""
    try:
        # Se usar package.json
        with open('package.json', 'r') as f:
            data = json.load(f)
            return data.get('version', '0.1.0')
    except:
        try:
            # Se usar version.txt
            with open('version.txt', 'r') as f:
                return f.read().strip()
        except:
            return '0.1.0'

def update_version(version_type='patch'):
    """Atualiza a versão baseada no tipo (major, minor, patch)"""
    current_version = get_current_version()
    
    # Parse da versão
    match = re.match(r'(\d+)\.(\d+)\.(\d+)', current_version)
    if not match:
        raise ValueError(f"Versão atual inválida: {current_version}")
    
    major, minor, patch = map(int, match.groups())
    
    # Incrementa baseado no tipo
    if version_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif version_type == 'minor':
        minor += 1
        patch = 0
    elif version_type == 'patch':
        patch += 1
    else:
        raise ValueError("Tipo de versão deve ser: major, minor ou patch")
    
    new_version = f"{major}.{minor}.{patch}"
    
    # Atualiza os arquivos
    update_version_files(new_version)
    
    return new_version

def update_version_files(version):
    """Atualiza a versão em todos os arquivos necessários"""
    
    # Atualiza package.json se existir
    if os.path.exists('package.json'):
        with open('package.json', 'r') as f:
            data = json.load(f)
        data['version'] = version
        with open('package.json', 'w') as f:
            json.dump(data, f, indent=2)
    
    # Atualiza/Cria version.txt
    with open('version.txt', 'w') as f:
        f.write(version)
    
    # Atualiza version.py para Django
    version_py_content = f'''
# Arquivo gerado automaticamente - NÃO EDITAR MANUALMENTE
__version__ = "{version}"
__build_date__ = "{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
__build_hash__ = "{get_git_short_hash()}"
'''
    
    with open('core/version.py', 'w') as f:
        f.write(version_py_content)
    
    print(f"✅ Versão atualizada para: {version}")

def get_git_short_hash():
    """Obtém o hash curto do commit atual"""
    try:
        result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], 
                              capture_output=True, text=True)
        return result.stdout.strip()
    except:
        return "unknown"

def create_git_tag(version):
    """Cria uma tag Git para a versão"""
    try:
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', f'🚀 Release v{version}'], check=True)
        subprocess.run(['git', 'tag', f'v{version}'], check=True)
        print(f"✅ Tag Git criada: v{version}")
    except Exception as e:
        print(f"⚠️  Não foi possível criar tag Git: {e}")

if __name__ == "__main__":
    import sys
    
    version_type = sys.argv[1] if len(sys.argv) > 1 else 'patch'
    
    if version_type not in ['major', 'minor', 'patch']:
        print("❌ Uso: python scripts/versioning.py [major|minor|patch]")
        sys.exit(1)
    
    new_version = update_version(version_type)
    create_git_tag(new_version)