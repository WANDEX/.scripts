#!/bin/sh
# Toggle between pulseeffects presets
OUTPUT_DIR="$HOME"'/.config/PulseEffects/output/'
OUTPUT_ARRAY=($( ls "$OUTPUT_DIR" | cut -f1 -d"." | sort -h | tr '\n' ' ' ))
OUTPUT_LENGTH=${#OUTPUT_ARRAY[@]}
COLORS_ARRAY=(7 5 13)
COLORS_LENGTH=${#COLORS_ARRAY[@]}
FILE="$HOME"'/.scripts/.temp/.toggle_preset_status.sh'
CURRENT_PRESET_NAME=$( "$FILE" | head -n 1 )
X_RES_COLORS_COUNT=$(($(xrdb -query | grep '*.color' | awk '{print $2}' | wc -w) - 1))

echo "${OUTPUT_ARRAY[@]}"
for (( i=0; i<$OUTPUT_LENGTH; i++ )); do
    # if count of predefined colors < available presets, append new color N
    if [[ "$COLORS_LENGTH" < "$OUTPUT_LENGTH" ]]; then
        random_int=$(shuf -i 1-"$X_RES_COLORS_COUNT" -n 1)
        COLORS_ARRAY+=("$random_int")
        COLORS_LENGTH=${#COLORS_ARRAY[@]}
    fi
    # find index of current preset out of all available presets
    if [[ "$CURRENT_PRESET_NAME" == "${OUTPUT_ARRAY[i]}" ]]; then
        # if there is no next element, get first
        if [[ -z "${OUTPUT_ARRAY[$i+1]}" ]]; then
            echo "${OUTPUT_ARRAY[0]}"
            NEW_PRESET_NAME="${OUTPUT_ARRAY[0]}"
            COLOR_INT="${COLORS_ARRAY[0]}"
        else
            echo "${OUTPUT_ARRAY[$i+1]}"
            NEW_PRESET_NAME="${OUTPUT_ARRAY[$i+1]}"
            COLOR_INT="${COLORS_ARRAY[$i+1]}"
        fi
    fi
done

# get Xresource color by N
X_RES_COLOR=$( xrdb -query | grep '*.color'"$COLOR_INT" | awk '{print $2}' )

# change preset (real)
pulseeffects -l "$NEW_PRESET_NAME"
# change at pulseeffects GUI (only preset name)
gsettings set com.github.wwmm.pulseeffects last-used-preset "$NEW_PRESET_NAME"
# write to file
printf "#!/bin/sh\necho '"$NEW_PRESET_NAME"'\necho '"$X_RES_COLOR"'" > "$FILE"
