from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from todo.models import Todo, ColorPriority, PriorityName
from todo.serializers import TodoCreateSerializer, TodoUpdateSerializer

import json

class TodoAPIView(APIView):
    @swagger_auto_schema(
        operation_summary="투두조회",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                required=True,
                type=openapi.TYPE_STRING,
                description='사용자 토큰'
            ),
            openapi.Parameter(
                'year',
                openapi.IN_QUERY,
                required=True,
                type=openapi.TYPE_STRING,
                description='년'
            ),
            openapi.Parameter(
                'month',
                openapi.IN_QUERY,
                required=True,
                type=openapi.TYPE_STRING,
                description='달'
            ),
            openapi.Parameter(
                'day',
                openapi.IN_QUERY,
                required=True,
                type=openapi.TYPE_STRING,
                description='일'
            ),
        ],
        responses={
            200: openapi.Response(
                description="투두조회",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER, description="응답코드"),
                        'priorit': openapi.Schema(type=openapi.TYPE_STRING, description="6자리 문자열(ex. 142356)"),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT,
                            properties={
                                '': openapi.Schema(type=openapi.TYPE_OBJECT,
                                    properties={
                                        'id': openapi.Schema(type=openapi.TYPE_STRING, description="고유번호"),
                                        'writer': openapi.Schema(type=openapi.TYPE_STRING, description="작성자 이메일"),
                                        'year': openapi.Schema(type=openapi.TYPE_STRING, description="년"),
                                        'month': openapi.Schema(type=openapi.TYPE_STRING, description="월"),
                                        'day': openapi.Schema(type=openapi.TYPE_STRING, description="일"),
                                        'title': openapi.Schema(type=openapi.TYPE_STRING, description="제목"),
                                        'description': openapi.Schema(type=openapi.TYPE_STRING, description="설명"),
                                        'done': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="완료여부"),
                                        'time': openapi.Schema(type=openapi.TYPE_STRING, description="설정한시간"),
                                        'color': openapi.Schema(type=openapi.TYPE_INTEGER, description="숫자 색"),
                                }),
                            },                        
                        ),
                    }    
                ),
            ),
            500: openapi.Response(
                description="조회실패",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER, description="응답코드"),
                    },
                ),
            ),
        },
     )
    #조회
    def get(self, request):
        user = request.user.email
        #사용자로부터 데이터 받기(year, month, day)
        d_year = request.GET['year']
        d_month = request.GET['month']
        d_day = request.GET['day']
        
        data = Todo.objects.filter(writer=str(request.user.email), year=d_year, month=d_month, day=d_day).values() #적절한 데이터 검색
        
        try:
            priority = ColorPriority.objects.get(writer=str(user)).priority
        except:
            priority = "123456"
        return Response({"resultCode":200,"data":data, "priority":priority}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="투두작성",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                required=True,
                type=openapi.TYPE_STRING,
                description='사용자 토큰'
            ),
            openapi.Parameter(
                'year',
                openapi.IN_QUERY,
                required=True,
                type=openapi.TYPE_STRING,
                description='년'
            ),
            openapi.Parameter(
                'month',
                openapi.IN_QUERY,
                required=True,
                type=openapi.TYPE_STRING,
                description='달'
            ),
            openapi.Parameter(
                'day',
                openapi.IN_QUERY,
                required=True,
                type=openapi.TYPE_STRING,
                description='일'
            ),
            openapi.Parameter(
                'title',
                openapi.IN_QUERY,
                required=True,
                type=openapi.TYPE_STRING,
                description='투두제목'
            ),
            openapi.Parameter(
                'color',
                openapi.IN_QUERY,
                required=True,
                type=openapi.TYPE_STRING,
                description='투두 Color'
            ),
        ],
        responses={
            200: openapi.Response(
                description="작성성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER, description="응답코드"),
                        'priorit': openapi.Schema(type=openapi.TYPE_STRING, description="6자리 문자열(ex. 142356)"),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_STRING, description="고유번호"),
                                'writer': openapi.Schema(type=openapi.TYPE_STRING, description="작성자 이메일"),
                                'year': openapi.Schema(type=openapi.TYPE_STRING, description="년"),
                                'month': openapi.Schema(type=openapi.TYPE_STRING, description="월"),
                                'day': openapi.Schema(type=openapi.TYPE_STRING, description="일"),
                                'title': openapi.Schema(type=openapi.TYPE_STRING, description="제목"),
                                'description': openapi.Schema(type=openapi.TYPE_STRING, description="설명"),
                                'done': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="완료여부"),
                                'time': openapi.Schema(type=openapi.TYPE_STRING, description="설정한시간"),
                                'color': openapi.Schema(type=openapi.TYPE_INTEGER, description="투두 Color"),
                            },                        
                        ),
                    }    
                ),
            ),
            500: openapi.Response(
                description="작성실패",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER, description="응답코드"),
                    },
                ),
            ),
        },
     )
    #추가
    def post(self, request):
        request.data["writer"] = request.user.email#writer추가
        #추가 작업
        serializer = TodoCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"resultCode":200,"data":serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"resultCode":500, "data":None}, status=status.HTTP_400_BAD_REQUEST)

    
    @swagger_auto_schema(
        operation_summary="투두수정([URL]/todo id)",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                required=True,
                type=openapi.TYPE_STRING,
                description='사용자 토큰'
            ),
            openapi.Parameter(
                'year',
                openapi.IN_QUERY,
                required=False,
                type=openapi.TYPE_STRING,
                description='년'
            ),
            openapi.Parameter(
                'month',
                openapi.IN_QUERY,
                required=False,
                type=openapi.TYPE_STRING,
                description='월'
            ),
            openapi.Parameter(
                'day',
                openapi.IN_QUERY,
                required=False,
                type=openapi.TYPE_STRING,
                description='일'
            ),
            openapi.Parameter(
                'title',
                openapi.IN_QUERY,
                required=False,
                type=openapi.TYPE_STRING,
                description='투두제목'
            ),
            openapi.Parameter(
                'color',
                openapi.IN_QUERY,
                required=False,
                type=openapi.TYPE_STRING,
                description='투두 Color'
            ),
            openapi.Parameter(
                'time',
                openapi.IN_QUERY,
                required=False,
                type=openapi.TYPE_STRING,
                description='투두시간'
            ),
            openapi.Parameter(
                'description',
                openapi.IN_QUERY,
                required=False,
                type=openapi.TYPE_STRING,
                description='투두설명'
            ),
            openapi.Parameter(
                'done',
                openapi.IN_QUERY,
                required=False,
                type=openapi.TYPE_BOOLEAN,
                description='투두 완료여부'
            ),
        ],
        responses={
            200: openapi.Response(
                description="작성성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER, description="응답코드"),
                    }    
                ),
            ),
            500: openapi.Response(
                description="작성실패",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER, description="응답코드"),
                    },
                ),
            ),
        },
     )
	#수정
    def put(self, request, pk):
        #todo = get_object_or_404(Todo, id=pk)
        todo = Todo.objects.get(id=pk)

        if todo.writer != str(request.user): #작성자 일치여부 확인
            return Response({"resultCode":500}, status=status.HTTP_400_BAD_REQUEST)
        
        #수정작업
        serializer = TodoUpdateSerializer.update(instance=todo, validated_data=request.data)
        
        result = {}
        result["title"] = serializer.title
        result["year"] = serializer.year
        result["month"] = serializer.month
        result["day"] = serializer.day
        result["title"] = serializer.title
        result["color"] = serializer.color #color
        result["description"] = serializer.description #description
        result["time"] = serializer.time #time
        result["id"] = serializer.id #id
        if str(serializer.done) == "1":
            result["done"] = True #done
        elif str(serializer.done) == "0":
            result["done"] = False
        else:
            result["done"] = serializer.done

        return Response({"resultCode":200,"data":result}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="투두삭제([URL]/todo id)",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                required=True,
                type=openapi.TYPE_STRING,
                description='사용자 토큰'
            ),
        ],
        responses={
            200: openapi.Response(
                description="삭제성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER, description="응답코드"),
                    }    
                ),
            ),
            500: openapi.Response(
                description="삭제실패",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER, description="응답코드"),
                    },
                ),
            ),
        },
     )
    #삭제
    def delete(self, request, pk):
        todo = Todo.objects.get(id=pk)
        print(todo)
        
        if todo.writer != str(request.user): #작성자 일치여부 확인
            return Response({"resultCode":500}, status=status.HTTP_400_BAD_REQUEST)
        
        #삭제작업
        todo.delete()
        return Response({"resultCode":200}, status=status.HTTP_200_OK)

class ColorView(APIView):
    def get(self, request):
        #사용자로부터 데이터 받기(year, month, day)
        d_year = request.GET['year']
        d_month = request.GET['month']
        user = request.user.email
        
        todo = Todo.objects.filter(writer=str(user), year=d_year, month=d_month)
        li = []
        for i in todo:
            li.append({"day":i.day ,"color":i.color})

        result = []
        for i in range(1, 31+1):
            fm = []
            for j in li:
                if j["day"] == i:
                    fm.append(j["color"])
            fm = list(set(fm)) #중복제거
            result.append({i:fm})
        return Response({"resultCode":200, "data":result}, status=status.HTTP_200_OK)

class ColorPriorityView(APIView):
    #우선순위 조회
    def get(self, request):
        user = request.user.email
        try:
            priority = ColorPriority.objects.get(writer=str(user))
        except:
            return Response({"resultCode":200, "data":"123456"}, status=status.HTTP_200_OK)
        return Response({"resultCode":200, "data":str(priority.priority)}, status=status.HTTP_200_OK)
    #우선순위 작성
    def post(self, request):
        priority = request.data["priority"]
        user = request.user.email
        
        if len(priority)!=6: #priority의 길이는 3
            return Response({"resultCode":500}, status=status.HTTP_200_OK)
    
        #작성작업
        buffer = ColorPriority.objects.filter(writer=str(user))
        if len(buffer) > 0:
            buffer.update(priority=priority)
            data = ColorPriority.objects.get(writer=str(user)).priority
        else:
            ColorPriority.objects.create(writer=str(user), priority=priority)
            data = ColorPriority.objects.get(writer=str(user)).priority
        return Response({"resultCode":200, "data": str(data)}, status=status.HTTP_200_OK)

class PriorityNameView(APIView):
    @swagger_auto_schema(
        operation_summary="우선순위이름 조회",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                required=True,
                type=openapi.TYPE_STRING,
                description='사용자 토큰'
            ),
        ],
        responses={
            200: openapi.Response(
                description="조회성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER, description="응답코드"),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT,
                            properties={
                                '1': openapi.Schema(type=openapi.TYPE_STRING, description="카테고리명1"),
                                '2': openapi.Schema(type=openapi.TYPE_STRING, description="카테고리명2"),
                                '3': openapi.Schema(type=openapi.TYPE_STRING, description="카테고리명3"),
                                '4': openapi.Schema(type=openapi.TYPE_STRING, description="카테고리명4"),
                                '5': openapi.Schema(type=openapi.TYPE_STRING, description="카테고리명5"),
                                '6': openapi.Schema(type=openapi.TYPE_STRING, description="카테고리명6"),
                            },                        
                        ),
                    }    
                ),
            ),
            500: openapi.Response(
                description="조회실패",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER, description="응답코드"),
                    },
                ),
            ),
        },
     )
    #우선순위 이름 조회
    def get(self, request):
        user = request.user.email
        try:
            priority = PriorityName.objects.get(writer=str(user))
            data = priority.names
        except:
            data = {
                    "1":"그룹 1",
                    "2":"그룹 2",
                    "3":"그룹 3",
                    "4":"그룹 4",
                    "5":"그룹 5",
                    "6":"그룹 6",
                }
            return Response({"resultCode":200, "data":data}, status=status.HTTP_200_OK)
        return Response({"resultCode":200, "data":data}, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="우선순위이름 작성(POST, json)",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                required=True,
                type=openapi.TYPE_STRING,
                description='사용자 토큰'
            ),
            openapi.Parameter(
                'priority',
                openapi.IN_QUERY,
                required=True,
                type=openapi.TYPE_OBJECT,
                description='key값=1~6까지 value는 각 카테고리명(json형식)'
            ),
        ],
        responses={
            200: openapi.Response(
                description="작성성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER, description="응답코드"),
                    }    
                ),
            ),
            500: openapi.Response(
                description="작성실패",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resultCode': openapi.Schema(type=openapi.TYPE_INTEGER, description="응답코드"),
                    },
                ),
            ),
        },
     )
    #우선순위 이름 작성
    def post(self, request):
        priority = request.data["priority"]
        user = request.user.email
        
        try:
            if priority["1"] and priority["2"] and priority["3"] and priority["4"] and priority["5"] and priority["6"]:
                pass
        except:
            return Response({"resultCode":500}, status=status.HTTP_200_OK)
        
        #작성작업
        buffer = PriorityName.objects.filter(writer=str(user))
        if len(buffer) > 0:
            buffer.update(names=priority)
        else:
            PriorityName.objects.create(writer=str(user), names=priority)
            
        return Response({"resultCode":200}, status=status.HTTP_200_OK)