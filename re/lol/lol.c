/**
 * @brief The source of the binary to be reversed.
 * @author Lloyd Gonzales (lgonzalesna@gmail.com)
 * 
 * This is the "reverse" of lol.py, which reconstructs the file in-memory and then
 * verifies that it matches the md5 contained in the file.
 * 
 * Naturally, because the file gets fully reconstructed, there's a lot of options
 * to recover the file. The original intent was that you're supposed to rebuild the
 * parser yourself by looking at the code in a decompiler and figuring out what the
 * file format is. But you could almost certainly do something like patching out the
 * binary to loop right after the file is reconstructed (but before the program exits),
 * dumping its memory, then looking for the file in its heap.
 * 
 * References:
 * - https://stackoverflow.com/questions/10324611/how-to-calculate-the-md5-hash-of-a-large-file-in-c
 */

#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#if defined(__APPLE__)
#  define COMMON_DIGEST_FOR_OPENSSL
#  include <CommonCrypto/CommonDigest.h>
#  define SHA1 CC_SHA1
#else
#  include <openssl/md5.h>
#endif

bool g_is_little_endian = false;

typedef struct {
    uint64_t file_length;
    unsigned char file_md5[MD5_DIGEST_LENGTH];
    char* data;
} lol_file_t;


/**
 * @brief Calculate the md5 sum of an array of bytes.
 * 
 * \param [in, out] digest The calculated md5 digest.
 * \param [in] data The data to calculate the md5 sum of.
 * \param [in] data_len The length of the data to calculate the md5 sum over.
 */
void calculate_md5(unsigned char digest[MD5_DIGEST_LENGTH], unsigned char data[], uint64_t data_len){
    MD5_CTX mdContext;

    MD5_Init(&mdContext);
    MD5_Update (&mdContext, data, data_len);
    MD5_Final (digest, &mdContext);
}

/**
 * \brief Print out an md5 digest to hex.
 * 
 * \param digest The md5 digest to print out. Should be exactly 16 bytes.
 */
void print_md5(unsigned char digest[MD5_DIGEST_LENGTH]){
    char out[33] = {0};
    for (int n = 0; n < 16; ++n) {
        snprintf(&(out[n*2]), 16*2, "%02x", (unsigned int)digest[n]);
    }
    printf("%s\n", out);
}

/**
 * @brief Check that two MD5 digests are equal.
 * 
 * this really only exists because these aren't null-terminated so strcmp()
 * doesn't work, but i'd also like to keep the clarity of MD5_DIGEST_LENGTH around
 * 
 * \param [in] digest_1 The first digest to compare.
 * \param [in] digest_2 The second digest to compare.
 * \retval true if the digests are equal
 * \retval false if the digest are not equal
 */
bool compare_md5(unsigned char digest_1[MD5_DIGEST_LENGTH], unsigned char digest_2[MD5_DIGEST_LENGTH]){
    for(int i = 0; i < MD5_DIGEST_LENGTH; i++){
        if(digest_1[i] != digest_2[i]){
            return false;
        }
    }

    return true;
}

/**
 * \brief If necessary, convert a BE uint32 to the machine's endianness.
 * 
 * Ref: https://stackoverflow.com/questions/2182002/how-to-convert-big-endian-to-little-endian-in-c-without-using-library-functions
 * 
 * \param [in] val A big-endian uint32.
 * \return uint32_t The correctly-interpreted value.
 */
uint32_t interpret_uint32(uint32_t val){
    if (g_is_little_endian){
        val = ((val << 8) & 0xFF00FF00 ) | ((val >> 8) & 0xFF00FF ); 
        return (val << 16) | (val >> 16);
    }

    return val;
}

/**
 * \brief If necessary, convert a BE uint64 to the machine's endianness.
 * 
 * Ref: https://stackoverflow.com/questions/2182002/how-to-convert-big-endian-to-little-endian-in-c-without-using-library-functions
 * 
 * \param [in] val A big-endian uint64.
 * \return uint64_t The correctly-interpreted value.
 */
uint64_t interpret_uint64(uint64_t val){
    if (g_is_little_endian){
        val = ((val << 8) & 0xFF00FF00FF00FF00ULL ) | ((val >> 8) & 0x00FF00FF00FF00FFULL );
        val = ((val << 16) & 0xFFFF0000FFFF0000ULL ) | ((val >> 16) & 0x0000FFFF0000FFFFULL );
        return (val << 32) | (val >> 32);
    }

    return val;
}

int main(int argc, char* argv[]){
    // Original file
    char* filename;
    FILE *fp;

    // Lolfile
    lol_file_t lolfile = {0};

    // Reconstructed info
    unsigned char* reconstructed_data;
    uint64_t cur_pos = 0;
    unsigned char reconstructed_md5[MD5_DIGEST_LENGTH];

    if (argc == 2){
        filename = argv[1];
    } else {
        printf("Usage: %s file.lol\n", argv[0]);
        exit(1);
    }

    // Check for endianness.
    int n = 1;
    // little endian if true
    if(*(char *)&n == 1){
        g_is_little_endian = true;
    }

    fp = fopen(filename, "rb");

    // Get file length.
    fread(&lolfile.file_length, sizeof(lolfile.file_length), 1, fp);
    lolfile.file_length = interpret_uint64(lolfile.file_length);
    
    // Get final MD5.
    fread(&lolfile.file_md5, sizeof(lolfile.file_md5), 1, fp);

    // Create the in-memory file.
    reconstructed_data = malloc(sizeof(unsigned char) * lolfile.file_length);

    assert(reconstructed_data != NULL);

    // At this point, fp is at the start of the first chunk. All we really
    // need to do now is start reading chunks off and seek back to the absolute
    // position whenever necessary.
    while(true){
        uint32_t chunk_length;
        uint64_t next_chunk;

        // Get length of chunk data.
        fread(&chunk_length, sizeof(chunk_length), 1, fp);
        chunk_length = interpret_uint32(chunk_length);

        // Check that the ending position of reading in this chunk won't overrun
        // the internal file's boundaries.
        if (cur_pos + chunk_length > lolfile.file_length){
            // Maybe this'll be a nice hint?
            printf("File is longer than expected, final pointer may be missing.\n");
            exit(1);
        }

        // Read that many into reconstructed_data, plus whatever the
        // current offset is.
        fread(reconstructed_data + cur_pos, chunk_length, 1, fp);
        cur_pos += chunk_length;

        // Figure out where the next chunk is.
        fread(&next_chunk, sizeof(next_chunk), 1, fp);
        next_chunk = interpret_uint64(next_chunk);

        // If the next chunk is "null", then break. Else, update fp to
        // that position.
        if (next_chunk == 0){
            // File has been reconstructed.
            break;
        } else {
            fseek(fp, next_chunk, SEEK_SET);
        }
    }

    // Check that the md5 sum is identical
    calculate_md5(reconstructed_md5, reconstructed_data, lolfile.file_length);
    if(compare_md5(reconstructed_md5, lolfile.file_md5)){
        printf("OK\n");
        exit(0);
    }else{
        printf("Check failed\n");
        exit(1);

        // Could leave these in to make it more obvious what's happening
        // print_md5(reconstructed_md5);
        // print_md5(lolfile.file_md5);
    }
}