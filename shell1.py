import os
import subprocess
import platform
import shlex
import sys
import re
from datetime import datetime


class WindowsShellEmulator:
    def __init__(self):
        self.current_dir = os.getcwd()
        self.running = True
        # Windows-like environment variables
        self.env_vars = {
            "PATH": os.environ.get("PATH", ""),
            "TEMP": os.environ.get("TEMP", "C:\\Windows\\Temp"),
            "USERPROFILE": os.environ.get("USERPROFILE", "C:\\Users\\User"),
            "SYSTEMROOT": "C:\\Windows",
            "SYSTEMDRIVE": "C:",
            "COMPUTERNAME": platform.node(),
            "USERNAME": os.environ.get("USERNAME", "User"),
            "PROMPT": "$P$G",  # Default Windows prompt format
        }
        self.commands = {
            "dir": self.cmd_dir,
            "cd": self.cmd_cd,
            "cls": self.cmd_cls,
            "copy": self.cmd_copy,
            "del": self.cmd_del,
            "echo": self.cmd_echo,
            "exit": self.cmd_exit,
            "help": self.cmd_help,
            "md": self.cmd_md,
            "mkdir": self.cmd_md,
            "move": self.cmd_move,
            "path": self.cmd_path,
            "prompt": self.cmd_prompt,
            "ren": self.cmd_ren,
            "rename": self.cmd_ren,
            "rd": self.cmd_rd,
            "rmdir": self.cmd_rd,
            "set": self.cmd_set,
            "time": self.cmd_time,
            "date": self.cmd_date,
            "type": self.cmd_type,
            "ver": self.cmd_ver,
            "vol": self.cmd_vol,
        }

    def run(self):
        """Main loop of the shell emulator"""
        print(f"Microsoft Windows Emulator [Version 10.0.19045.3803]")
        print(f"(c) Microsoft Corporation. All rights reserved.\n")
        
        while self.running:
            # Format prompt based on current directory and prompt setting
            prompt = self.format_prompt()
            try:
                # Get user input
                command = input(prompt)
                
                # Skip empty commands
                if not command.strip():
                    continue
                
                # Process the command
                self.process_command(command)
                
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit the shell.")
            except Exception as e:
                print(f"Error: {str(e)}")

    def format_prompt(self):
        """Format the command prompt based on the PROMPT environment variable"""
        prompt_format = self.env_vars.get("PROMPT", "$P$G")
        
        # Replace Windows prompt special characters
        prompt = prompt_format.replace("$P", self.current_dir)
        prompt = prompt.replace("$G", ">")
        prompt = prompt.replace("$L", "<")
        prompt = prompt.replace("$N", self.env_vars.get("SYSTEMDRIVE", "C:"))
        prompt = prompt.replace("$D", datetime.now().strftime("%a %m/%d/%Y"))
        prompt = prompt.replace("$T", datetime.now().strftime("%H:%M:%S.%f")[:-3])
        prompt = prompt.replace("$V", "10.0.19045.3803")  # Windows version
        prompt = prompt.replace("$_", "\n")
        prompt = prompt.replace("$$", "$")
        
        return prompt + " "

    def process_command(self, command_line):
        """Process a command entered by the user"""
        # Handle piping, redirection, etc. later
        
        # Parse command and arguments
        parts = self.parse_command_line(command_line)
        if not parts:
            return
            
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Process environment variable expansion
        command = self.expand_env_vars(command)
        args = [self.expand_env_vars(arg) for arg in args]
        
        # Execute built-in command if it exists
        if command in self.commands:
            self.commands[command](args)
        else:
            # Try to execute as an external command
            self.execute_external_command(command, args)

    def parse_command_line(self, command_line):
        """Parse a command line into command and arguments"""
        # Handle quotes and escapes
        try:
            if platform.system() == "Windows":
                # Windows-style parsing
                return shlex.split(command_line, posix=False)
            else:
                # Unix-style parsing but try to be Windows-compatible
                return shlex.split(command_line, posix=True)
        except ValueError as e:
            print(f"Error parsing command: {str(e)}")
            return []

    def expand_env_vars(self, text):
        """Expand environment variables in Windows style (%VAR%)"""
        if text and "%" in text:
            # Find all environment variables (pattern: %VAR%)
            matches = re.findall(r'%([^%]+)%', text)
            expanded_text = text
            
            for var_name in matches:
                if var_name.upper() in self.env_vars:
                    expanded_text = expanded_text.replace(
                        f"%{var_name}%", self.env_vars[var_name.upper()]
                    )
            
            return expanded_text
        return text

    def execute_external_command(self, command, args):
        """Try to execute an external command"""
        try:
            # Combine command and args
            cmd_with_args = [command] + args
            
            # Get the current environment and update with our emulated env vars
            env = os.environ.copy()
            for key, value in self.env_vars.items():
                env[key] = value
            
            # Execute the command
            process = subprocess.run(
                cmd_with_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.current_dir,
                env=env,
                shell=True
            )
            
            # Output results
            if process.stdout:
                print(process.stdout.rstrip())
            if process.stderr:
                print(process.stderr.rstrip())
                
            # Return code handling
            if process.returncode != 0:
                print(f"Command exited with code {process.returncode}")
                
        except FileNotFoundError:
            print(f"'{command}' is not recognized as an internal or external command, operable program or batch file.")
        except Exception as e:
            print(f"Error executing command: {str(e)}")

    # Command implementations
    def cmd_dir(self, args):
        """Implement the DIR command"""
        path = "." if not args else args[0]
        
        try:
            # Get directory contents
            items = os.listdir(path)
            total_files = 0
            total_dirs = 0
            total_size = 0
            
            # Print header
            print(f" Directory of {os.path.abspath(path)}\n")
            
            # Print directory contents
            for item in sorted(items):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    size = "<DIR>"
                    total_dirs += 1
                else:
                    size = os.path.getsize(item_path)
                    total_size += size
                    size = f"{size:,}"
                    total_files += 1
                
                # Get file/dir timestamp
                timestamp = os.path.getmtime(item_path)
                date_str = datetime.fromtimestamp(timestamp).strftime("%m/%d/%Y  %I:%M %p")
                
                # Format output like Windows CMD
                if os.path.isdir(item_path):
                    print(f"{date_str}    {size:>10}  {item}")
                else:
                    print(f"{date_str}    {size:>10}  {item}")
            
            # Print summary
            print(f"{total_files:14,} File(s)  {total_size:,} bytes")
            print(f"{total_dirs:14,} Dir(s)")
            
        except FileNotFoundError:
            print(f"The system cannot find the path specified: {path}")
        except PermissionError:
            print(f"Access denied: {path}")
        except Exception as e:
            print(f"Error: {str(e)}")

    def cmd_cd(self, args):
        """Change directory command"""
        # If no args, just print current directory
        if not args:
            print(self.current_dir)
            return
            
        # Get target directory
        target = args[0]
        
        # Handle parent directory
        if target == "..":
            new_dir = os.path.dirname(self.current_dir)
        # Handle drive letter changes
        elif len(target) == 2 and target[1] == ':':
            drive = target[0].upper()
            # In a real Windows system we would check if the drive exists
            new_dir = f"{drive}:\\"
        # Handle absolute and relative paths
        else:
            if os.path.isabs(target):
                new_dir = target
            else:
                new_dir = os.path.join(self.current_dir, target)
        
        # Check if directory exists
        if os.path.isdir(new_dir):
            self.current_dir = os.path.normpath(new_dir)
        else:
            print(f"The system cannot find the path specified: {target}")

    def cmd_cls(self, args):
        """Clear screen command"""
        # Clear screen based on OS
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")

    def cmd_copy(self, args):
        """Copy file command"""
        if len(args) < 2:
            print("The syntax of the command is incorrect.")
            return
            
        source = args[0]
        destination = args[1]
        
        try:
            # Check if source exists
            if not os.path.exists(source):
                print(f"The system cannot find the file specified: {source}")
                return
                
            # If destination is a directory, use the source filename
            if os.path.isdir(destination):
                destination = os.path.join(destination, os.path.basename(source))
                
            # Perform the copy
            with open(source, 'rb') as src_file:
                with open(destination, 'wb') as dst_file:
                    dst_file.write(src_file.read())
                    
            print(f"        1 file(s) copied.")
            
        except PermissionError:
            print("Access denied.")
        except Exception as e:
            print(f"Error: {str(e)}")

    def cmd_del(self, args):
        """Delete file command"""
        if not args:
            print("The syntax of the command is incorrect.")
            return
            
        for pattern in args:
            try:
                if os.path.isfile(pattern):
                    os.remove(pattern)
                else:
                    print(f"The system cannot find the file specified: {pattern}")
            except PermissionError:
                print(f"Access denied: {pattern}")
            except Exception as e:
                print(f"Error: {str(e)}")

    def cmd_echo(self, args):
        """Echo command"""
        if not args:
            print("ECHO is on.")
            return
            
        # Join all arguments with spaces
        output = ' '.join(args)
        
        # Check for echo state command
        if output.lower() in ("on", "off"):
            print(f"ECHO is now {output}")
            return
            
        # Print the output
        print(output)

    def cmd_exit(self, args):
        """Exit the shell"""
        self.running = False
        print("Exiting Windows shell emulator.")

    def cmd_help(self, args):
        """Show help information"""
        if not args:
            print("For more information on a specific command, type HELP command-name")
            print("\nAvailable commands:")
            # Display commands in columns
            cmd_list = sorted(self.commands.keys())
            col_width = max(len(cmd) for cmd in cmd_list) + 2
            num_cols = 4
            for i in range(0, len(cmd_list), num_cols):
                row = cmd_list[i:i+num_cols]
                print(''.join(cmd.ljust(col_width) for cmd in row))
        else:
            command = args[0].lower()
            if command in self.commands:
                print(f"\nHelp for {command}:")
                doc = self.commands[command].__doc__ or "No help available."
                print(doc)
            else:
                print(f"This command is not supported by the help utility.")

    def cmd_md(self, args):
        """Make directory command"""
        if not args:
            print("The syntax of the command is incorrect.")
            return
            
        for directory in args:
            try:
                os.makedirs(directory, exist_ok=True)
            except PermissionError:
                print(f"Access denied: {directory}")
            except Exception as e:
                print(f"Error: {str(e)}")

    def cmd_move(self, args):
        """Move file command"""
        if len(args) < 2:
            print("The syntax of the command is incorrect.")
            return
            
        source = args[0]
        destination = args[1]
        
        try:
            # Check if source exists
            if not os.path.exists(source):
                print(f"The system cannot find the file specified: {source}")
                return
                
            # If destination is a directory, use the source filename
            if os.path.isdir(destination):
                destination = os.path.join(destination, os.path.basename(source))
                
            # Perform the move
            os.rename(source, destination)
            print(f"        1 file(s) moved.")
            
        except PermissionError:
            print("Access denied.")
        except Exception as e:
            print(f"Error: {str(e)}")

    def cmd_path(self, args):
        """Display or set PATH variable"""
        if not args:
            print(f"PATH={self.env_vars['PATH']}")
        else:
            # Set the PATH variable
            self.env_vars['PATH'] = ' '.join(args)
            print(f"PATH={self.env_vars['PATH']}")

    def cmd_prompt(self, args):
        """Change command prompt"""
        if not args:
            print(f"PROMPT={self.env_vars['PROMPT']}")
        else:
            # Set the PROMPT variable
            self.env_vars['PROMPT'] = ' '.join(args)

    def cmd_ren(self, args):
        """Rename file command"""
        if len(args) < 2:
            print("The syntax of the command is incorrect.")
            return
            
        source = args[0]
        destination = args[1]
        
        try:
            # Check if source exists
            if not os.path.exists(source):
                print(f"The system cannot find the file specified: {source}")
                return
                
            # Perform the rename
            os.rename(source, destination)
            
        except PermissionError:
            print("Access denied.")
        except Exception as e:
            print(f"Error: {str(e)}")

    def cmd_rd(self, args):
        """Remove directory command"""
        if not args:
            print("The syntax of the command is incorrect.")
            return
            
        for directory in args:
            try:
                os.rmdir(directory)
            except FileNotFoundError:
                print(f"The system cannot find the directory: {directory}")
            except OSError:
                print(f"The directory is not empty: {directory}")
            except PermissionError:
                print(f"Access denied: {directory}")
            except Exception as e:
                print(f"Error: {str(e)}")

    def cmd_set(self, args):
        """Set or display environment variables"""
        # If no arguments, display all environment variables
        if not args:
            for name, value in sorted(self.env_vars.items()):
                print(f"{name}={value}")
            return
            
        # Parse variable assignment
        var_string = ' '.join(args)
        if '=' in var_string:
            name, value = var_string.split('=', 1)
            self.env_vars[name.upper()] = value
        else:
            # Display specific variable if it exists
            var_name = var_string.upper()
            if var_name in self.env_vars:
                print(f"{var_name}={self.env_vars[var_name]}")
            else:
                print(f"Environment variable {var_name} not defined")

    def cmd_time(self, args):
        """Display or set system time"""
        print(f"Current time: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")

    def cmd_date(self, args):
        """Display or set system date"""
        print(f"Current date: {datetime.now().strftime('%a %m/%d/%Y')}")

    def cmd_type(self, args):
        """Display contents of a text file"""
        if not args:
            print("The syntax of the command is incorrect.")
            return
            
        filename = args[0]
        try:
            with open(filename, 'r') as file:
                print(file.read(), end='')
        except FileNotFoundError:
            print(f"The system cannot find the file specified: {filename}")
        except UnicodeDecodeError:
            print(f"The file {filename} is not a text file.")
        except Exception as e:
            print(f"Error: {str(e)}")

    def cmd_ver(self, args):
        """Display Windows version"""
        print("\nMicrosoft Windows Emulator [Version 10.0.19045.3803]")

    def cmd_vol(self, args):
        """Display disk volume information"""
        drive = self.current_dir[0].upper() if self.current_dir else "C"
        print(f" Volume in drive {drive} is Windows")
        print(f" Volume Serial Number is 1A2B-3C4D")


if __name__ == "__main__":
    shell = WindowsShellEmulator()
    shell.run()
