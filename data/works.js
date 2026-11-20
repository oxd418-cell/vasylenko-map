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
   ===================================================================== */
var IMG=[
 "assets/works/1-nautilus.webp",
 "assets/works/2-tablet.webp",
 "assets/works/3-brick-oval.webp",
 "assets/works/4-red-figure.webp",
 "assets/works/5-egg.webp"
];

var W=[
 {id:1,x:14.5,y:75.0,t:{uk:"Робота 1",en:"Work 1"},d:{uk:"Тут буде коротка фраза про цю роботу. Це тестовий текст.",en:"A short line about this work will go here. This is placeholder text."},ok:true,img:0},
 {id:2,x:25.0,y:31.0,t:{uk:"Робота 2",en:"Work 2"},d:{uk:"Одна-дві фрази про об’єкт. Без інструкцій, як це сприймати.",en:"One or two sentences about the piece. No instructions on how to see it."},ok:true,img:1},
 {id:3,x:29.5,y:28.6,t:{uk:"Робота 3",en:"Work 3"},d:{uk:"Знак може повторюватися: кожне місце має власну точку й власний QR.",en:"A sign can repeat: every spot has its own pin and its own QR."},ok:true,img:2},
 {id:4,x:19.8,y:70.2,t:{uk:"Робота 4",en:"Work 4"},d:{uk:"Тестовий текст про четверту роботу.",en:"Placeholder text about the fourth work."},ok:true,img:3},
 {id:5,x:12.2,y:66.8,t:{uk:"Робота 5",en:"Work 5"},d:{uk:"Тестовий текст про п’яту роботу.",en:"Placeholder text about the fifth work."},ok:true,img:4},
 {id:6,x:32.0,y:35.5,t:{uk:"Робота 6",en:"Work 6"},d:{uk:"Тестовий повтор: той самий знак, що й у роботі 4, але на іншому місці.",en:"Test repeat: the same sign as work 4, in a different place."},ok:true,img:3},
 {id:7,x:22.5,y:67.0,t:{uk:"Робота 7",en:"Work 7"},d:{uk:"Тестовий повтор: той самий знак, що й у роботі 2, але на іншому місці.",en:"Test repeat: the same sign as work 2, in a different place."},ok:true,img:1},
 {id:8,x:26.5,y:37.6,t:{uk:"Робота 8",en:"Work 8"},d:{uk:"Тестовий повтор: той самий знак, що й у роботі 5, але на іншому місці.",en:"Test repeat: the same sign as work 5, in a different place."},ok:true,img:4},
 {id:9,x:34.5,y:31.8,t:{uk:"Робота 9",en:"Work 9"},d:{uk:"Тестовий повтор: той самий знак, що й у роботі 1, але на іншому місці.",en:"Test repeat: the same sign as work 1, in a different place."},ok:true,img:0},
 {id:10,x:21.5,y:76.2,t:{uk:"Робота 10",en:"Work 10"},d:{uk:"Тестовий повтор: той самий знак, що й у роботі 3, але на іншому місці.",en:"Test repeat: the same sign as work 3, in a different place."},ok:true,img:2},
 {id:11,x:26.5,y:51.0,t:{uk:"Тест: зниклий об’єкт",en:"Test: a vanished piece"},d:{uk:"Так виглядатиме робота, якої вже немає. Ми приймаємо це як частину проєкту.",en:"This is how a work that is no longer there will look. We accept this as part of the project."},ok:false,img:-1}
];
