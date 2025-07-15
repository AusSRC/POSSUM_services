# POSSUM database backups

Cron jobs for periodically creating backup files of the database. The setup for this periodic pgdump and backup is very manual.

Process:

0. Download cron inside container and on the VM
1. Inside the database container, run a cron job to regularly create a pgdump of the POSSUM database
2. Inside the VM (outside the container), use `rclone` to copy the contents of the backup folder to the objectstore

## Setup

Install cron with the following (should not need `sudo` when running this command inside of the container)

```
sudo apt update && sudo apt install cron
```

### Database backup

Then, SSH into the database container `docker exec -it possum_db /bin/bash` and install cron as well. Copy the `pgdump.sh` file into the `/home/` directory and create a cron job that runs weekly. You may also need to install `vim` or another editor of your choice to be able to update the cron table.

```
crontab -e
0 0 * * 1 /home/pgdump.sh
```

This will make backups weekly where the date is the filename. The backups will be stored at `/var/lib/postgresql/data/backups` which is mounted to `/data/backups` on the VM. We will do the Acacia upload from the VM.

### Acacia upload

You will need to copy your Acacia bucket access key to the VM under `~/.config/rclone/rclone.conf`. And you may also need to install rclone `sudo apt install rclone` on the VM. Then you should be able to list the contents of the the bucket where you would like to upload your backups. Once you have your access set up, you can create another crontab entry (also weekly) to upload all of the contents of `/data/backups` to the objectstore (in this case, to `pawsey0587:aussrc-backups/possum`).

```
crontab -e
0 0 * * 1 /home/ubuntu/POSSUM_services/backups/acacia_upload.sh
```

## Restore

To restore the database from a dump you can use the following command:

```
psql -U admin -d possum < 01.04.2025.dump
```
