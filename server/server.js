const express = require("express");
const cors = require("cors");
const nodemailer = require("nodemailer");
const jwt = require("jsonwebtoken");
const cron = require("node-cron");

require("dotenv").config();

const app = express();


app.use(
  cors({
    origin:"http://localhost:5173",
    credentials:true
  })
);


app.use(express.json());



const transporter = nodemailer.createTransport({

  service:"gmail",

  auth:{
    user:process.env.EMAIL_USER,
    pass:process.env.EMAIL_PASS
  }

});



let reminders = [
  {
    id:1,
    title:"Xây dựng API FastAPI cho chatbot",
    type:"Bài tập",
    email:"vothithaingoc072005@gmail.com",
    remindTime:new Date("2026-06-24 22:00"),
    deadline:"23:59 27/06/2026",
    status:"Chờ gửi",
    sent:false
  },

  {
    id:2,
    title:"Thi kết thúc môn Perl & Python",
    type:"Lịch thi",
    email:"vothithaingoc072005@gmail.com",
    remindTime:new Date("2026-07-01 08:00"),
    deadline:"07:00 04/07/2026",
    status:"Chờ gửi",
    sent:false
  }
];





app.post("/send-email",async(req,res)=>{

 try{

  const {
    email,
    subject,
    text
  }=req.body;



  await transporter.sendMail({

    from:process.env.EMAIL_USER,

    to:email,

    subject,

    text

  });



  res.json({

    success:true,

    message:"Gui thanh cong"

  });



 }catch(error){

  console.log(error);


  res.status(500).json({

    success:false,

    message:"Gui that bai"

  });


 }

});







app.post("/api/reminders", (req,res)=>{


 const reminder={

  id:Date.now(),

  title:req.body.title,

  type:req.body.type,

  email:req.body.email,

  remindTime:new Date(req.body.remindTime),

  deadline:req.body.deadline,

  status:"Chờ gửi",

  sent:false

 };


 reminders.push(reminder);



 res.json({

  success:true,

  reminder

 });


});







app.get("/api/reminders",(req,res)=>{


 res.json({

  success:true,

  reminders

 });


});








cron.schedule("* * * * *",async()=>{


 console.log("Kiem tra nhac nho...");


 const now=new Date();



 for(let reminder of reminders){


  if(
    reminder.sent===false &&
    reminder.remindTime<=now
  ){


   try{


    await transporter.sendMail({

      from:process.env.EMAIL_USER,

      to:reminder.email,

      subject:
      `Nhắc nhở học tập - ${reminder.title}`,

      text:

`Xin chào,

Bạn có lịch ${reminder.type}:

${reminder.title}

Deadline:

${reminder.deadline}

Vui lòng hoàn thành đúng hạn.

StudyMate`

    });



    reminder.sent=true;

    reminder.status="Đã gửi";


    console.log(
      "Da gui:",
      reminder.title
    );



   }catch(error){


    console.log(
      "Loi gui mail:",
      error
    );


   }


  }


 }



});








app.post("/api/auth/login",async(req,res)=>{


 const {
  email,
  password
 }=req.body;



 if(
 email==="vothithaingoc072005@gmail.com"
 &&
 password==="123456"
 ){



 const user={

  id:1,

  email,

  name:"Admin"

 };



 const token=jwt.sign(

  user,

  process.env.JWT_SECRET || "secret_key",

  {
    expiresIn:"1d"
  }

 );



 try{


 await transporter.sendMail({

  from:process.env.EMAIL_USER,

  to:email,

  subject:"Thông báo đăng nhập",

  text:
  `Xin chào ${user.name}, bạn vừa đăng nhập StudyMate.`

 });


 }catch(error){}



 return res.json({

  success:true,

  token,

  user

 });



 }



 res.status(401).json({

  success:false,

  message:"Sai email hoac mat khau"

 });


});








app.get("/api/auth/me",(req,res)=>{


 const token=req.headers.authorization;



 if(!token){

  return res.status(401).json({

   message:"Chua dang nhap"

  });

 }



 try{


 const user=jwt.verify(

  token.split(" ")[1],

  process.env.JWT_SECRET || "secret_key"

 );


 res.json({

  success:true,

  user

 });


 }catch(error){


 res.status(401).json({

  message:"Token sai"

 });


 }


});

app.get("/",(req,res)=>{

 res.send("Server dang chay");

});

console.log(
"Loaded server.js - EMAIL REMINDER READY"
);

app.listen(

 process.env.PORT || 8000,

 ()=>{

 console.log(
 `Server running at http://localhost:${process.env.PORT || 8000}`
 );

}

);