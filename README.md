# Final Project

An exercise to put to practice software development teamwork, subsystem communication, containers, deployment, and CI/CD pipelines. See [instructions](./instructions.md) for details.

![Back End CI](https://github.com/software-students-spring2025/5-final-hihi/actions/workflows/back_end.yml/badge.svg)
![Front End CI](https://github.com/software-students-spring2025/5-final-hihi/actions/workflows/front_end.yml/badge.svg)

# HiHi Recipe 
---

## Team Members
- **Eli Sun**: [IDislikeName](https://github.com/IDislikeName)
- **Jasmine Zhang**: [Jasminezhang666666](https://github.com/Jasminezhang666666)
- **Yifan Zhang**: [YifanZZZZZZ](https://github.com/YifanZZZZZZ)
- **Shuyuan Yang**: [shuyuanyyy](https://github.com/shuyuanyyy)

---

## Project Overview 📝

HiHi recipe is a containerized web application that allows users to record audio in the browser, and detects the emotional content analyzing by machine learning models.

---

## Setup Instructions 📌

### 1. Clone the Repository

```bash
git clone https://github.com/software-students-spring2025/5-final-hihi.git
cd 5-final-hihi
```


### 2. Start the System with Docker

```bash
docker-compose build --no-cache
docker-compose up  
```

### 3. Visit the Web through Browser

```bash
http://127.0.0.1:6000
```

---

## References 📎
The recipe dataset is from Kaggle [Food.com Recipes](https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions/data), which is a dataset consisting of 180K+ recipes from Food.com. 
