//
//  main.c
//  Assignment1
//
//  Created by 김형순 on 05/09/2019.
//  Copyright © 2019 김형순. All rights reserved.
//

#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>


#define CONTACT_NUM 100000
#define LINE_LENGTH 100
#define NAME_LENGTH 20


int binary_search(char **names, const char* target, int total_nums);
int compare(const void *a, const void *b);
int sort_contact(char **names);
int get_names(char **names);
void search_name(char **names, const char* target, int total_nums);
int delete_name(char **names, const char* target, int total_nums, int option);
int insertion(char **names, const char* name, const char* number, int total_nums, int option);
int modify(char **names, const char* target, const char* name, const char* number, int total_nums);

int main(int argc, const char * argv[]) {
    FILE *fp;
    char **names = NULL;
    char buffer[LINE_LENGTH];
    char buffer2[LINE_LENGTH];
    char buffer3[LINE_LENGTH];
    int total_nums = 0, i = 0, option = 0;
    
    // Allocate memory to store entities as array
    names = malloc(sizeof(char*)*CONTACT_NUM);
    for (i = 0; i<CONTACT_NUM; i++) {
        names[i] = malloc(sizeof(char)*LINE_LENGTH);
    }
    
    // sort contact.csv file only if file do not exist.
    if(!(fp = fopen("2015004493_김형순.csv", "r+"))){
        printf("start creating 2015004493_김형순.csv\n");
        if((total_nums = sort_contact(names)) < 0){
            printf("Couldn't get contact.csv file data.\n");
            return -1;
        };
        fp = fopen("2015004493_김형순.csv", "r+");
    }
    
    // Read total_nums
    fgets(buffer, LINE_LENGTH, fp);
    buffer[strlen(buffer)-1] = '\0';
    total_nums = atoi(buffer);
    
    // Read entities
    for (i=0; i<total_nums; i++) {
        strcpy(names[i], fgets(buffer, LINE_LENGTH, fp));
    }
    
    fclose(fp);
    
    while (1) {
        // Print menu
        printf("**********************\n");
        printf("Select option\n1. search by name\n2. insert\n3. delete\n4. Modify\n5. exit\n");
        printf("**********************\n\n");
        scanf("%d", &option);
        fgets(buffer, NAME_LENGTH, stdin);
        switch (option) {
            case 1:
                printf("Type name: ");
                strcpy(buffer, "");
                fgets(buffer, NAME_LENGTH, stdin);
                buffer[strlen(buffer)-1] = '\0';
                
                // Check input name is Hangul
                if (!(buffer[0] & 0x80)){
                    printf("You only can use Hangul as name\n");
                    break;
                }
                
                search_name(names, buffer, total_nums);
                break;
                
            case 2:
                printf("Type name: ");
                strcpy(buffer, "");
                fgets(buffer, NAME_LENGTH, stdin);
                buffer[strlen(buffer)-1] = '\0';
                
                // Check input name is Hangul
                if (!(buffer[0] & 0x80)){
                    printf("You only can use Hangul as name\n");
                    break;
                }
                
                printf("Type number: ");
                strcpy(buffer2, "");
                fgets(buffer2, NAME_LENGTH, stdin);
                buffer2[strlen(buffer2)-1] = '\0';
                
                
                total_nums = insertion(names, buffer, buffer2, total_nums, 0);
                break;
                
            case 3:
                printf("Type name: ");
                strcpy(buffer, "");
                fgets(buffer, NAME_LENGTH, stdin);
                buffer[strlen(buffer)-1] = '\0';
                
                // Check input name is Hangul
                if (!(buffer[0] & 0x80)){
                    printf("You only can use Hangul as name\n");
                    break;
                }
                
                total_nums = delete_name(names, buffer, total_nums, 0);
                break;
                
            case 4:
                printf("Type name to modify: ");
                strcpy(buffer, "");
                fgets(buffer, NAME_LENGTH, stdin);
                buffer[strlen(buffer)-1] = '\0';
                
                // Check input name is Hangul
                if (!(buffer[0] & 0x80)){
                    printf("You only can use Hangul as name\n");
                    break;
                }
                
                printf("Type name to be modified: ");
                strcpy(buffer3, "");
                fgets(buffer3, NAME_LENGTH, stdin);
                buffer3[strlen(buffer3)-1] = '\0';
                
                // Check input name is Hangul
                if (!(buffer3[0] & 0x80)){
                    printf("You only can use Hangul as name\n");
                    break;
                }
                
                printf("Type number to be modified: ");
                strcpy(buffer2, "");
                fgets(buffer2, NAME_LENGTH, stdin);
                buffer2[strlen(buffer2)-1] = '\0';
                total_nums = modify(names, buffer, buffer3, buffer2, total_nums);
                break;
                
            case 5:
                printf("exit program\n");
                for (i = 0; i<total_nums; i++) {
                    free(names[i]);
                }
                free(names);
                return 0;
                
            default:
                break;
        }
    }
    return 0;
}

/**
 *  Function for get location of searching name by using binary search
 *
 *  @param[in]  names       array of entity in phone book
 *  @param[in]  target      name to search
 *  @param[in]  total_nums  the number entity in phone book
 *  @return     returns exact or one before location of target on phone bool
 */
int binary_search(char **names, const char* target, int total_nums){
    
    int mid = total_nums/2, begin = 0, end = total_nums-1, cmp = 0;
    char temp[LINE_LENGTH];
    
    // Search with binary search algorithm
    while (1) {
        strcpy(temp, names[mid]);
        cmp = strcmp(target, strtok(temp, ","));
        // Exact match
        if (cmp == 0) {
            return mid;
        }
        // Near match for inserting and partial match
        else if (begin > end){
            if (cmp < 0) {
                return mid -1;
            }
            else{
                return mid;
            }
        }
        else{
            if (cmp < 0){
                end = mid - 1;
                mid = (begin + end) / 2;
            }
            else{   // cmp > 0
                begin = mid + 1;
                mid = (begin + end) / 2;
            }
        }
    }
}

/**
 *  Function for compare two string which will be used in sorting
 *
 *  @param[in]  a   first operand
 *  @param[in]  b   second operand
 *  @return     0 if two operand are same, negative if a < b positive if a > b
 */
int compare(const void *a, const void *b){
    const char *pa = *(const char**)a;
    const char *pb = *(const char**)b;
    return strcmp(pa,pb);
}

/**
 *  Initialize phone book sort data in contact.csv as descending order
 *  and store data to 2015004493_김형순.csv
 *
 *  @param[in]  names   array of entity in phone book
 *  @return     0 if two operand are same, negative if a < b positive if a > b
 */
int sort_contact(char **names){
    FILE *fp;
    FILE *fp2;
    char buffer[LINE_LENGTH];
    int len = LINE_LENGTH, i = 0;
    
    if((fp= fopen("contact.csv", "r")) < 0 || (fp2 = fopen("2015004493_김형순.csv", "w")) < 0){
        printf("Couldn't open file\n");
        return -1;
    }
    if(!fgets(buffer, len, fp)){
        fclose(fp);
        fclose(fp2);
        return -1;
    }
    // Read each line from file and store them to array
    while (fgets(buffer, len, fp)) {
        strcpy(names[i], buffer);
        i++;
    }
    // If reading was not compeletly done, give error
    if (i != 50000) {
        fclose(fp);
        fclose(fp2);
        return -1;
    }
    // Sort data as descending order and save to file
    qsort((void *)names, 50000, sizeof(names[0]), compare);
    fprintf(fp2, "%d\n", i);
    i = 0;
    while (i<50000) {
        if(!fputs(names[i], fp2)){
            fclose(fp);
            fclose(fp2);
            return -1;
        }
        i++;
    }
    
    fclose(fp);
    fclose(fp2);
    
    return 1;
}

/**
 *  Function for search entire or partial name from phone book
 *  Print every name which is partially matched with target
 *
 *  @param[in]  names       array of entity in phone book
 *  @param[in]  target      name to search
 *  @param[in]  total_nums  the number entity in phone book
 */
void search_name(char **names, const char* target, int total_nums){
    int i = binary_search(names, target, total_nums);
    int check1 = 0, check2 = 0;
    char *p = strstr(names[i], target);
    
    // Check and print name which is entirely matched
    if(p != NULL && p == names[i]){
        printf("%s", names[i]);
        check1++;
    }
    i++;
    // Check and print name which is partially matched
    p = strstr(names[i], target);
    check2 = i;
    while (p != NULL && p == names[i]) {
        printf("%s", names[i]);
        i++;
        p = strstr(names[i], target);
    }
    
    // If there is no matched name, print error message
    if (check1 == 0 && check2 == i) {
        printf("There is no search result.\n");
    }
}

/**
 *  Delete one entity which is exactly matched with target
 *
 *  @param[in,out]  names       array of entity in phone book
 *  @param[in]  target      name to search
 *  @param[in]  total_nums  the number entity in phone book
 *  @param[in]  option      0 if user calls, 1 if used in modify function
 *  @return     updated total_num
 */
int delete_name(char **names, const char* target, int total_nums, int option){
    FILE *fp;
    int i;
    char temp[LINE_LENGTH];
    
    i = binary_search(names, target, total_nums);
    strcpy(temp, names[i]);
    
    // Check name is exactly matched or not
    if (strcmp(strtok(temp, ","), target) != 0) {
        printf("There is no name matched. Deletion failed.\n");
        return total_nums;
    }
    else{
        // Update name array
        for (i = i + 1; i<total_nums; i++) {
            strcpy(names[i-1], names[i]);
        }
        strcpy(names[total_nums - 1], "");
        total_nums --;
        
        // Update file
        fp = fopen("2015004493_김형순.csv", "w");
        fseek(fp, 0, SEEK_SET);
        fprintf(fp, "%d\n", total_nums);
        for (i = 0; i<total_nums; i++) {
            fputs(names[i], fp);
        }
        fclose(fp);
        
         if (option == 0) {
            printf("Deletion completed\n");
        }
        
        return total_nums;
    }
}

/**
 *  Insert new entity with new name and new number
 *
 *  @param[in,out]  names       array of entity in phone book
 *  @param[in]  name        name to insert
 *  @param[in]  number      number to insert
 *  @param[in]  total_nums  the number entity in phone book
 *  @param[in]  option      0 if user calls, 1 if used in modify function
 *  @return     updated total num
 */
int insertion(char **names, const char* name, const char* number, int total_nums, int option){
    FILE *fp;
    int check = 1, j = 0;
    unsigned long i = 0;
    char new_name[LINE_LENGTH];
    
    // Check input number is appropirate format.
    if (atoi(number) != 0){
        if (strlen(number) == 11 && strncmp(number, "010", 3) ==0) {
            check = 0;
        }
    }

    if (strlen(name) > NAME_LENGTH) {
        printf("Too long name. Name should be under 20 words\n");
        return total_nums;
    }
    
    if (check != 0) {
        printf("You should enter exact form of number\nLike 010xxxxxxxx\n");
        return total_nums;
    }
    
    strcpy(new_name, name);
    strcat(new_name, ",");
    strcat(new_name, number);
    strcat(new_name, "\n");
    
    // Search appropirate location to store/
    i = binary_search(names, name, total_nums);
    i++;
    // Update names array
    for (j = total_nums; j > i; j--) {
        strcpy(names[j], names[j-1]);
    }
    // Insert input name to array
    strcpy(names[i], new_name);
    
    total_nums ++;
    //Update file
    fp = fopen("2015004493_김형순.csv", "w");
    fseek(fp, 0, SEEK_SET);
    fprintf(fp, "%d\n", total_nums);
    for (i = 0; i<total_nums; i++) {
        fputs(names[i], fp);
    }
    
    fclose(fp);
    
    if (option == 0) {
        printf("Insertion completed\nName: %s\nNumber: %s\n", name, number);
    }
    
    return total_nums;
}

/**
 *  Modify one entity which is exactly matched or first partially matched
 *
 *  @param[in,out]  names       array of entity in phone book
 *  @param[in]  target      name to modify
 *  @param[in]  name        name to insert
 *  @param[in]  number      number to insert
 *  @param[in]  total_nums  the number entity in phone book
 *  @return     updated total num
 */
int modify(char **names, const char* target, const char* name, const char* number, int total_nums){
    
    int temp_total = total_nums;
    
    // Check deletion will be valid
    int i = binary_search(names, target, total_nums);
    char *deleting = NULL;
    char temp[LINE_LENGTH];
    
    // If target is not entirely matched, check the next name.
    if ((deleting = strstr(names[i], target)) == NULL){
        // If the next name is not matched too, it means there is no match.
        if ((deleting = strstr(names[i+1], target)) == NULL){
            printf("There is no name matched.\n");
            return total_nums;
        }
    }
    
    // Now 'deleting' will be entire matched name if it exist.
    // If not, the first partial match name will be.
    // Parse name part from names
    strcpy(temp, deleting);
    
    temp_total = insertion(names, name, number, temp_total, 1);
    
    // If insertion was failed.
    if(temp_total == total_nums){
        return total_nums;
    }
    temp_total = delete_name(names, strtok(temp, ","), temp_total, 1);
    
    
    printf("Modification completed\nName: %s\nNumber: %s\n", name, number);
    
    return temp_total;
}

