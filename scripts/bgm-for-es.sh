#!/usr/bin/env bash

# This file is part of the microplay-hub
# Designs by Liontek1985
# for RetroPie and offshoot
#
# The RetroPie Project is the legal property of its developers, whose names are
# too numerous to list here. Please refer to the COPYRIGHT.md file distributed with this source.
#
# See the LICENSE.md file at the top-level directory of this distribution and
# at https://raw.githubusercontent.com/RetroPie/RetroPie-Setup/master/LICENSE.md
#
# bgm-for-es script v1.1 - 2023-11-21

rp_module_id="bgm-for-es"
rp_module_desc="Background Music for ES"
rp_module_repo="git https://github.com/microplay-hub/bgm-for-es.git main"
rp_module_section="main"
rp_module_flags="noinstclean"

function sources_bgm-for-es() {
    gitPullOrClone
}

function depends_bgm-for-es() {
    local depends=(cmake python3-pip)
     getDepends "${depends[@]}"
}

function sources_bgm-for-es() {
    if [[ -d "$md_inst" ]]; then
        git -C "$md_inst" reset --hard  # ensure that no local changes exist
    fi
    gitPullOrClone "$md_inst"
}

function install_bgm-for-es() {
	mkdir "$datadir/musics"
	ln -s "$datadir/musics" "$datadir/music"
    chown -cR pi:pi "$datadir/music"
	chmod 755 "$datadir/music"
	
    cd "$md_inst"
	
    if [[ ! -f "$configdir/all/$md_id.cfg" ]]; then
        iniConfig "=" '"' "$configdir/all/$md_id.cfg"
        iniSet "CFGFOLDER" "music"
        iniSet "CFGDELAY" "0"
        iniSet "CFGREST" "yes"
    fi
    chown $user:$user "$configdir/all/$md_id.cfg"
	chmod 755 "$configdir/all/$md_id.cfg"
	
    cd "$home"
	chown -cR pi:pi "/opt/retropie/configs"
	curl -sSL https://raw.githubusercontent.com/microplay-hub/bgm-for-es/main/scripts/install-esbgm.py | sudo -u pi python3 -
	rm "$datadir/retropiemenu/Disable background music.sh"
	rm "$datadir/retropiemenu/Enable background music.sh"
	rm "$md_inst/scripts/bgm-for-es.sh"
}

function remove_bgm-for-es() {
    cd "$home"
	python3 install-esbgm.py --uninstall
    cd "$md_inst"
    rm-r "$configdir/all/$md_id.cfg"
	rm -rf "$md_inst"
	rm "install-esbgm.py"
	rm -rf "/home/pi/.config/esbgm"
}

function configini_bgm-for-es() {
	chown $user:$user "$configdir/all/$md_id.cfg"	
    iniConfig "=" '"' "$configdir/all/$md_id.cfg"	
}


function changefolder_bgm-for-es() {
    options=(
        F1 "Change Folder to RetroPie/music"
        F2 "Change Folder to RetroPie/musics"
		X "[current setting: $cfgfolder]"
    )
    local cmd=(dialog --backtitle "$__backtitle" --menu "Choose an option." 22 86 16)
    local choice=$("${cmd[@]}" "${options[@]}" 2>&1 >/dev/tty)

    case "$choice" in
        F1)
			iniSet "CFGFOLDER" "music"
			sed -i -e 5c"musicdir: ~/RetroPie/music" $home/.config/esbgm/config.yaml
            ;;
        F2)
			iniSet "CFGFOLDER" "musics"
			sed -i -e 5c"musicdir: ~/RetroPie/musics" $home/.config/esbgm/config.yaml
            ;;
    esac
}

function changerest_bgm-for-es() {
    options=(
        R1 "Change Auto-Music-Restart to -YES-"
        R2 "Change Auto-Music-Restart to -NO-"
		X "[current setting: $cfgrest]"
    )
    local cmd=(dialog --backtitle "$__backtitle" --menu "Choose an option." 22 86 16)
    local choice=$("${cmd[@]}" "${options[@]}" 2>&1 >/dev/tty)

    case "$choice" in
        R1)
			iniSet "CFGREST" "YES"
			sed -i "9s~.*~restart: yes~" $home/.config/esbgm/config.yaml
            ;;
        R2)
			iniSet "CFGREST" "NO"
			sed -i "9s~.*~restart: no~" $home/.config/esbgm/config.yaml
            ;;
    esac
}

function changedelay_bgm-for-es() {

			iniGet "CFGDELAY"
			sed -i "2s~.*~startdelay: $cfgdelay~" $home/.config/esbgm/config.yaml

}

function gui_bgm-for-es() {
    local cmd=(dialog --backtitle "$__backtitle" --menu "Choose an option." 22 86 16)
	
	    iniConfig "=" '"' "$configdir/all/$md_id.cfg"
		
        iniGet "CFGFOLDER"
        local cfgfolder=${ini_value}
        iniGet "CFGDELAY"
        local cfgdelay=${ini_value}
        iniGet "CFGREST"
        local cfgrest=${ini_value}

	
    local options=(
        A "Disable Background-Music"
        B "Enable Background-Music"
        C "Editing the Config-File"
    )
        options+=(
			CF "Change Folder - (now: $cfgfolder)"
			CD "Change Startdelay - (now: $cfgdelay)"
			CR "Change Music-Restart - (now: $cfgrest)"
            TEK "### Script by Liontek1985 ###"
            )	
	
	
	
    local choice=$("${cmd[@]}" "${options[@]}" 2>&1 >/dev/tty)
	
	    iniConfig "=" '"' "$configdir/all/$md_id.cfg"
		
        iniGet "CFGFOLDER"
        local cfgfolder=${ini_value}
        iniGet "CFGDELAY"
        local cfgdelay=${ini_value}
        iniGet "CFGREST"
        local cfgrest=${ini_value}
		
	
	
    if [[ -n "$choice" ]]; then
        case "$choice" in
            A)
				mkdir -p "$home/.config/esbgm"
				touch "$home/.config/esbgm/disable.flag"
                ;;		
            B)
				rm -f "$home/.config/esbgm/disable.flag"
                ;;
            C)
				editFile "$home/.config/esbgm/config.yaml"
                ;;
            CF)
				configini_bgm-for-es
				changefolder_bgm-for-es
                ;;
            CD)
				cfgdelay=$(dialog --title "Change Startdelay" --clear --rangebox "Configure the Startdelay in Seconds" 0 120 5 120 30 2>&1 >/dev/tty)
                    if [[ -n "$cfgdelay" ]]; then
                        iniSet "CFGDELAY" "${cfgdelay//[^[:digit:]]/}"
                    fi

				configini_bgm-for-es
				changedelay_bgm-for-es			
                ;;	
            CR)
				configini_bgm-for-es
				changerest_bgm-for-es
                ;;
				
        esac
    fi
}