/* =====================================================================
   РОБОТИ НА МАПІ — редагувати тут
   ---------------------------------------------------------------------
   id   — номер роботи. QR під роботою веде на адресу сайту + #w<id>
          (наприклад https://.../#w3)
   x, y — де стоїть кружечок на мапі, у відсотках від ширини і висоти
          картинки assets/map.jpg (0,0 — лівий верхній кут)
   t    — назва (uk / en)
   d    — короткий опис (uk / en)
   ok   — true: висить; false: зникла (показується пунктирним кружком)
   img  — номер картинки з масиву IMG нижче (0 — перша), -1 — без картинки
   IAR  — пропорції (ширина/висота) кожної картинки; від них залежить розмір фігурки на мапі
   ===================================================================== */
var IMG=[
 "assets/works/w01.webp",
 "assets/works/w02.webp",
 "assets/works/w03.webp",
 "assets/works/w04.webp",
 "assets/works/w05.webp",
 "assets/works/w06.webp",
 "assets/works/w07.webp",
 "assets/works/w08.webp",
 "assets/works/w09.webp",
 "assets/works/w10.webp",
 "assets/works/w11.webp",
 "assets/works/w12.webp",
 "assets/works/w13.webp",
 "assets/works/w14.webp",
 "assets/works/w15.webp",
 "assets/works/w16.webp",
 "assets/works/w17.webp",
 "assets/works/w18.webp",
 "assets/works/w19.webp"
];
var IAR=[0.739, 0.58, 1.023, 0.329, 4.291, 4.906, 4.692, 4.274, 4.7, 3.266, 1.866, 3.259, 4.532, 4.532, 3.565, 0.959, 1.74, 4.311, 1.734];

var W=[
 {id:1,x:14,y:74,t:{uk:"Робота 1",en:"Work 1"},d:{uk:"Тут буде коротка фраза про цю роботу. Це тестовий текст.",en:"A short line about this work will go here. This is placeholder text."},ok:true,img:0},
 {id:2,x:26,y:72,t:{uk:"Робота 2",en:"Work 2"},d:{uk:"Тут буде коротка фраза про цю роботу. Це тестовий текст.",en:"A short line about this work will go here. This is placeholder text."},ok:true,img:1},
 {id:3,x:38,y:75,t:{uk:"Робота 3",en:"Work 3"},d:{uk:"Тут буде коротка фраза про цю роботу. Це тестовий текст.",en:"A short line about this work will go here. This is placeholder text."},ok:true,img:2},
 {id:4,x:50,y:78,t:{uk:"Робота 4",en:"Work 4"},d:{uk:"Тут буде коротка фраза про цю роботу. Це тестовий текст.",en:"A short line about this work will go here. This is placeholder text."},ok:true,img:3},
 {id:5,x:17,y:82,t:{uk:"Робота 5",en:"Work 5"},d:{uk:"Тут буде коротка фраза про цю роботу. Це тестовий текст.",en:"A short line about this work will go here. This is placeholder text."},ok:true,img:4},
 {id:6,x:29,y:81,t:{uk:"Робота 6",en:"Work 6"},d:{uk:"Тут буде коротка фраза про цю роботу. Це тестовий текст.",en:"A short line about this work will go here. This is placeholder text."},ok:true,img:5},
 {id:7,x:41,y:84,t:{uk:"Робота 7",en:"Work 7"},d:{uk:"Тут буде коротка фраза про цю роботу. Це тестовий текст.",en:"A short line about this work will go here. This is placeholder text."},ok:true,img:6},
 {id:8,x:53,y:87,t:{uk:"Робота 8",en:"Work 8"},d:{uk:"Тут буде коротка фраза про цю роботу. Це тестовий текст.",en:"A short line about this work will go here. This is placeholder text."},ok:true,img:7},
 {id:9,x:22,y:90,t:{uk:"Робота 9",en:"Work 9"},d:{uk:"Тут буде коротка фраза про цю роботу. Це тестовий текст.",en:"A short line about this work will go here. This is placeholder text."},ok:true,img:8},
 {id:10,x:34,y:92,t:{uk:"Робота 10",en:"Work 10"},d:{uk:"Тут буде коротка фраза про цю роботу. Це тестовий текст.",en:"A short line about this work will go here. This is placeholder text."},ok:true,img:9},
 {id:11,x:26,y:20,t:{uk:"Робота 11",en:"Work 11"},d:{uk:"Тут буде коротка фраза про цю роботу. Це тестовий текст.",en:"A short line about this work will go here. This is placeholder text."},ok:true,img:10},
 {id:12,x:40,y:16,t:{uk:"Робота 12",en:"Work 12"},d:{uk:"Тут буде коротка фраза про цю роботу. Це тестовий текст.",en:"A short line about this work will go here. This is placeholder text."},ok:true,img:11},
 {id:13,x:54,y:22,t:{uk:"Робота 13",en:"Work 13"},d:{uk:"Тут буде коротка фраза про цю роботу. Це тестовий текст.",en:"A short line about this work will go here. This is placeholder text."},ok:true,img:12},
 {id:14,x:31,y:29,t:{uk:"Робота 14",en:"Work 14"},d:{uk:"Тут буде коротка фраза про цю роботу. Це тестовий текст.",en:"A short line about this work will go here. This is placeholder text."},ok:true,img:13},
 {id:15,x:45,y:28,t:{uk:"Робота 15",en:"Work 15"},d:{uk:"Тут буде коротка фраза про цю роботу. Це тестовий текст.",en:"A short line about this work will go here. This is placeholder text."},ok:true,img:14},
 {id:16,x:59,y:31,t:{uk:"Робота 16",en:"Work 16"},d:{uk:"Тут буде коротка фраза про цю роботу. Це тестовий текст.",en:"A short line about this work will go here. This is placeholder text."},ok:true,img:15},
 {id:17,x:25,y:38,t:{uk:"Робота 17",en:"Work 17"},d:{uk:"Тут буде коротка фраза про цю роботу. Це тестовий текст.",en:"A short line about this work will go here. This is placeholder text."},ok:true,img:16},
 {id:18,x:39,y:37,t:{uk:"Робота 18",en:"Work 18"},d:{uk:"Тут буде коротка фраза про цю роботу. Це тестовий текст.",en:"A short line about this work will go here. This is placeholder text."},ok:true,img:17},
 {id:19,x:53,y:38,t:{uk:"Робота 19",en:"Work 19"},d:{uk:"Тут буде коротка фраза про цю роботу. Це тестовий текст.",en:"A short line about this work will go here. This is placeholder text."},ok:true,img:18},
 {id:20,x:44,y:58,t:{uk:"Тест: зниклий об’єкт",en:"Test: a vanished piece"},d:{uk:"Так виглядатиме робота, якої вже немає. Ми приймаємо це як частину проєкту.",en:"This is how a work that is no longer there will look. We accept this as part of the project."},ok:false,img:-1}
];
