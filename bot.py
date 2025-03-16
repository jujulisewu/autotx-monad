#!/usr/bin/env python3
import os
import shareithub
import sys
import asyncio
from shareithub import shareithub
from asyncio.subprocess import PIPE
from subprocess import CalledProcessError
from colorama import init, Fore, Style
from dotenv import load_dotenv

init(autoreset=True)
load_dotenv()

PRIVATE_KEY = os.getenv("PRIVATE_KEY")

def display_header():
    print(Style.BRIGHT + Fore.CYAN + "======================================")
    print(Style.BRIGHT + Fore.CYAN + " AUTO TX MONAD BY SHARE IT HUB        ")
    print(Style.BRIGHT + Fore.CYAN + "====================================\n")

shareithub()

def check_env_vars():
    required_vars = ["PRIVATE_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(Fore.RED + f"❌ Missing environment variables: {', '.join(missing_vars)}")
        for var in missing_vars:
            value = input(f"Masukkan nilai untuk {var}: ").strip()
            if value:
                os.environ[var] = value
            else:
                print(Fore.RED + f"❌ {var} tidak boleh kosong!")
                sys.exit(1)

check_env_vars()

module_folder = "./modules"
if not os.path.isdir(module_folder):
    print(Fore.RED + f"Folder '{module_folder}' tidak ditemukan!")
    sys.exit(1)

module_files = [f for f in os.listdir(module_folder) if f.endswith(".py")]

scripts = []
for filename in module_files:
    name = os.path.splitext(filename)[0].title()
    path = os.path.join(module_folder, filename)
    scripts.append({ "name": name, "path": path })

async def run_script(script):
    print(Fore.YELLOW + f"\n📜 Menjalankan: {script['name']}...")
    cmd = [sys.executable, script["path"]]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=PIPE,
        stderr=PIPE
    )
    stdout, stderr = await proc.communicate()

    if stdout:
        print(Fore.WHITE + stdout.decode())
    if stderr:
        print(Fore.RED + "Error: " + stderr.decode())

    if proc.returncode == 0:
        print(Fore.GREEN + f"✅ Berhasil: {script['name']}")
    else:
        print(Fore.RED + f"❌ Gagal: {script['name']} (Kode keluar: {proc.returncode})")
        raise CalledProcessError(proc.returncode, cmd)

async def run_scripts_sequentially(loop_count, selected_scripts):
    for i in range(loop_count):
        print(Fore.BLUE + f"\n🔄 Loop {i + 1} dari {loop_count}...\n")
        for script in selected_scripts:
            try:
                await run_script(script)
            except Exception as e:
                print(Fore.RED + f"⚠️ Melewati {script['name']} karena error")

async def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    display_header()
    print(Fore.BLUE + Style.BRIGHT + "\n🚀 Jalankan Modul Auto\n")
    print("Pilih modul yang ingin dijalankan (pisahkan dengan koma, misal: 1,2,3).")
    print("Jika dikosongkan, maka semua modul akan dijalankan.\n")
    for idx, script in enumerate(scripts, start=1):
        print(f"{idx}. {script['name']}")
    selection = input("\nMasukkan nomor modul (default semua): ").strip()

    if selection == "":
        selected_modules = scripts
    else:
        try:
            indices = [int(x.strip()) for x in selection.split(",") if x.strip().isdigit()]
            selected_modules = [scripts[i - 1] for i in indices if 1 <= i <= len(scripts)]
            if not selected_modules:
                selected_modules = scripts
        except Exception as e:
            selected_modules = scripts

    loop_count_str = input("\nBerapa kali ingin menjalankan modul? (default 1): ").strip()
    try:
        loop_count = int(loop_count_str) if loop_count_str != "" else 1
        if loop_count <= 0:
            print("Masukkan angka lebih dari 0. Menggunakan default 1.")
            loop_count = 1
    except:
        loop_count = 1

    print(Fore.GREEN + f"\n🚀 Memulai eksekusi {len(selected_modules)} modul selama {loop_count} loop\n")

    await run_scripts_sequentially(loop_count, selected_modules)
    print(Fore.GREEN + Style.BRIGHT + "\n✅✅ Semua modul selesai dijalankan! ✅✅\n")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(Fore.RED + "\nProgram dihentikan oleh user.")
        sys.exit(0)
