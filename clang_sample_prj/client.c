#include <stdio.h>
#include <stdlib.h>
#include <WinSock2.h>
#define _CRT_SECURE_NO_WARNINGS
#define WIN32_LEAN_AND_MEAN

#pragma comment(lib, "Ws2_32.lib")
#define BUF_SIZE 1024

int main(int argc, char **argv)
{
    int num;
    WSADATA wsaData;
    struct sockaddr_in server_addr;
    SOCKET s;

    if (argc != 4)
    {
        printf("Command parameter does not right.\n");
        exit(1);
    }

    WSAStartup(MAKEWORD(2, 2), &wsaData);

    if ((s = socket(PF_INET, SOCK_STREAM, 0)) < 0)
    {
        printf("Socket Creat Error.\n");
        exit(1);
    }

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = inet_addr(argv[1]);
    server_addr.sin_port = htons(atoi(argv[2]));

    if (connect(s, (SOCKADDR *)&server_addr, sizeof(server_addr)) == SOCKET_ERROR)
    {
        printf("Socket Connection Error.\n");
        exit(1);
    }

    printf("File Send Start\n");

    int sendBytes;
    long totalSendBytes;
    long file_size;
    char buf[BUF_SIZE];
    char SendFilesize;

    FILE *fp;
    fp = fopen(argv[3], "rb"); // 파일 읽기 모드
    if (fp == NULL)
    {
        printf("File not Exist");
        exit(1);
    }

    fseek(fp, 0, SEEK_END); // 파일 포인터의 마지막 위치를 기준으로 이동
    file_size = ftell(fp);  // 파일 포인터의 위치로 파일의 크기 구하기
    fseek(fp, 0, SEEK_SET); // 파일의 처음 위치를 기준으로 이동
    totalSendBytes = 0;

    printf("In progress: %d/%dByte(s) [%d%%]\n", totalSendBytes, file_size, (totalSendBytes * 100 / file_size));

    SendFilesize = _snprintf(buf, sizeof(buf), "%d", file_size); // snprintf()는 사이즈를 체크할 수 있기 때문에
                                                                 // 사이즈 커져 생길 수 있는 오류를 미리 예방할 수 있다.
    send(s, buf, SendFilesize, 0);                               // 파일 크기 전송

    while ((sendBytes = fread(buf, sizeof(char), sizeof(buf), fp)) > 0) // 남은 데이터가 없을 때 까지 반복
    {
        send(s, buf, sendBytes, 0);  // 버퍼사이즈 만큼 서버에 데이터 보냄
        totalSendBytes += sendBytes; // 보낸 데이터 누적
        printf("In progress: %d/%dByte(s) [%d%%]\n", totalSendBytes, file_size, (totalSendBytes * 100 / file_size));
    }
    printf("File send successed");

    closesocket(s);
    WSACleanup();

    return 0;
}
