#include <stdio.h>
#include <stdlib.h>
#include <WinSock2.h>
#include <windows.h>
#include <process.h>
#include <iostream>

#define _CRT_SECURE_NO_WARNINGS
#define WIN32_LEAN_AND_MEAN

#pragma comment(lib, "Ws2_32.lib")
#define BUF_SIZE 1024

using namespace std;

SOCKET s_listen, s_accept;

int main(int argc, char **argv)
{
    WSADATA wsaData;
    struct sockaddr_in local_addr;

    if (argc != 3)
    {
        printf("Command parameter does not right.\n");
        exit(1);
    }

    WSAStartup(MAKEWORD(2, 2), &wsaData);

    if ((s_listen = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    {
        printf("Socket Creat Error.\n");
        exit(1);
    }

    memset(&local_addr, 0, sizeof(local_addr));
    local_addr.sin_family = AF_INET;
    local_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    local_addr.sin_port = htons(atoi(argv[1]));

    if (bind(s_listen, (SOCKADDR *)&local_addr, sizeof(local_addr)) == SOCKET_ERROR)
    {
        printf("Socket Bind Error.\n");
        exit(1);
    }

    if (listen(s_listen, 5) == SOCKET_ERROR)
    {
        printf("Socket Listen Error.\n");
        exit(1);
    }

    printf("This server is listening... \n");

    struct sockaddr_in client_addr;
    int len_addr = sizeof(client_addr);
    int readBytes;
    long file_size;
    long totalReadBytes;

    char buf[BUF_SIZE];

    FILE *fp;
    fp = fopen(argv[2], "wb");

    s_accept = accept(s_listen, (SOCKADDR *)&client_addr, &len_addr);

    if (s_accept)
    {
        printf("Connection Request from Client [IP:%s, Port:%d] has been Accepted\n",
               inet_ntoa(client_addr.sin_addr), ntohs(client_addr.sin_port));

        readBytes = recv(s_accept, buf, BUF_SIZE, 0); // 파일 크기를 받아옴
        file_size = atol(buf);                        // 파일 크기 형변환 char -> long

        totalReadBytes = 0;
        printf("In progress: %d/%dByte(s) [%d%%]\n", totalReadBytes, file_size, (totalReadBytes * 100 / file_size));

        while (totalReadBytes != file_size)
        {
            readBytes = recv(s_accept, buf, BUF_SIZE, 0); // 버퍼 사이즈만큼 클라이언트에서 데이터 받기
            totalReadBytes += readBytes;                  // 받은 데이터 누적
            printf("In progress: %d/%dByte(s) [%d%%]\n", totalReadBytes, file_size, (totalReadBytes * 100 / file_size));
            fwrite(buf, sizeof(char), readBytes, fp); // 파일에 받은 데이터 쓰기

            if (readBytes == SOCKET_ERROR)
            {
                printf("File Receive Error");
                exit(1);
            }
        }

        closesocket(s_accept);
        printf("File recieve successed");
    }
    else
    {
        printf("File Accept Error");
    }

    closesocket(s_listen);
    WSACleanup();

    return 0;
}