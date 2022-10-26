from pymediainfo import MediaInfo
import os

dirloc = "Directory\\where\\videos\\are\\located"  # change this

for f in os.listdir(dirloc):
    if f.endswith(".mp4"):
        media_info = MediaInfo.parse(os.path.join(dirloc, f))

        for track in media_info.tracks:
            if track.track_type == "Video":
                with open("Path\\Filename.nfo", "a") as nfo:  # and this
                    print("\n",
                          "====== " + f + " =====\n",
                          "\n"
                          "\n\tGeneral\n"
                          "\tTitle.....................: " + f[21:-4].replace('.', ' '), "\n"
                          "\tBit rate..................: {t.bit_rate}\n"
                          "\tFirst aired...............: \n"
                          "\tFormat....................: {t.format}\n"
                          "\tFormat Version............: {t.format_version}\n"
                          "\tFormat info...............: {t.format_info}\n"
                          "\tFile size.................:\n"
                          "\tDuration..................: {t.other_duration[0]} seconds\n"
                          "\tBit rate..................: {t.bit_rate}\n"
                          "\tEncoded date..............: {t.encoded_date}\n"
                          "\tWriting application.......: HandBrake 1.5.1 2022011000\n"
                          "\n"
                          "\tVideo\n"
                          "\tID........................: {t.track_id}\n"
                          "\tFormat....................: {t.other_format[0]}\n"
                          "\tCodec ID..................: {t.codec_id}\n"
                          "\tCodec ID/Info.............: {t.codec_id_info}\n"
                          "\tBit rate..................: {t.other_bit_rate[0]}\n"
                          "\tWidth.....................: {t.width}\n"
                          "\tHeight....................: {t.height}\n"
                          "\tDisplay aspect ratio......: {t.display_aspect_ratio}\n"
                          "\tFrame rate mode...........: {t.frame_rate_mode}\n"
                          "\tFrame rate................: {t.frame_rate}\n"
                          "\tFrame count...............: {t.frame_count}\n"
                          "\tChroma subsampling........: {t.chroma_subsampling}\n"
                          "\tBit depth.................: {t.bit_depth}"
                          "\n".format(t=track), file=nfo)

            elif track.track_type == "Audio":
                with open("Path\\Filename.nfo", "a") as nfo:  # and this
                    print("\tAudio\n"
                          "\tID........................: {t.track_id}\n"
                          "\tFormat....................: {t.format} {t.format_additionalfeatures}\n"
                          "\tFormat/info...............: {t.format_info}\n"
                          "\tCodec ID..................: {t.codec_id}\n"
                          "\tBit rate mode.............: {t.bit_rate_mode}\n"
                          "\tBit rate..................: {t.bit_rate}\n"
                          "\tChannels..................: {t.channel_s}\n"
                          "\tChannel layout............: {t.channel_layout}\n"
                          "\tSampling rate.............: {t.sampling_rate}\n"
                          "\tFrame rate................: {t.frame_rate}\n"
                          "\tCompression mode..........: {t.compression_mode}\n"
                          "\tTitle.....................: {t.title}\n"
                          "\tLanguage..................: {t.language}\n"
                          "\n Plot Summary:\n =============\n\n\n".format(t=track), file=nfo)
