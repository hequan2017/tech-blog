---
title: "typescript 基本类型 | Symbol | 接口| 函数| 泛型-- 学习笔记二"
date: "2019-03-16 20:14:18"
category: "typescript"
source: "https://blog.51cto.com/hequan/2364148"
---
> **内容介绍**
>
> TypeScript 学习笔记第二篇，系统梳理 TS 基础语法：布尔/数字/字符串/数组/元组/枚举/any/void/never/object 等基本类型与类型断言，Symbol 的唯一值与全局注册用法，接口（可选属性、索引签名、继承），函数类型别名、默认参数与重载，以及泛型函数与泛型约束。
>
> **技术备注**
>
> 文中语法在 TS 3.x 至当前 5.x 均有效；注意尖括号断言 `<string>target` 在 .tsx 文件中与 JSX 冲突，建议统一用 `as` 语法。tslint 已废弃，tsconfig 建议开启 strict。

---

### typescript 基本类型 | Symbol | 接口| 函数 -- 学习笔记二

#### 基本类型

```typescript
let bool:boolean = false
let num:number = 123
let str:string
str = "abc"
str = `数值是${num}`

let arr1: number[] = [1,2,3]
let arr2: Array<number | string > = [1,2,3]
let arr3: (string | number)[] = ['a',2,'c']

let tuple: [string,number,boolean] = ['a',2,true]

// 枚举
enum Roles {
    SUPER_ADMIN = 0,
    ADMIN,
    USER
}

// any类型
let value: any
value = "123"
const arr4: any[]=[1,'b']

// void类型

let v: void = undefined

const consoleText=(text: string): void =>{
    console.log(text)
}
consoleText("abc")

// null  undefined
let u: undefined = undefined
let n: null  = null

// never类型
const errorFunc = (message: string): never =>{
    throw new Error(message)
}
const infiniterFunc =():never =>{
    while(true){}
}
let neverVariable = (()=>{
    while(true){}
})

// object
let obj:object = {
    name : 'hequan',
}

// 类型断言
const  getLength = (target:string | number) : number =>{
    if ((<string>target).length || (target as string).length === 0){
        return (<string>target).length
    }else{
        return target.toString().length
    }
}
```

#### Symbol

```typescript
const s = Symbol("name") //唯一的值

const info ={
[s]:'hequan'
}
info[s]='123'
Object.getOwnPropertySymbols(info)
Reflect.ownKeys(info)

const s1 = Symbol.for('he') // 全局注册 先查找是否存在，没有再创建
Symbol.keyFor(s1) // 只查找 for创建的
```

#### 接口

tslint 配置（VS Code 设置 `"tslint.autoFixOnSave": true`，执行 `tslint --init` 生成）：

```json
{
    "root": false,
    "defaultSeverity": "error",
    "extends": [
        "tslint:recommended"
    ],
    "jsRules": {},
    "rules": {
        "quotemark": [false],
        "semicolon": [false],
        "interface-name": [true, "never-prefix"],
        "object-literal-sort-keys": [false]
    },
    "rulesDirectory": []
}
```

接口示例：

```typescript
interface NameInfo {
    firstName?: string, // ? 可选
    lastName: string,  // readonly lastName: string,
    [prop: string]: any
}

const getFullName = ({ firstName, lastName}: NameInfo): string => {
    return `${firstName}${lastName}`
}

getFullName({
    firstName: "he",
    lastName: "quan",
    other: 1,
} as NameInfo)

interface RoleDic {
    [id: string]: string,
}

const role: RoleDic = {
    0: 'super_admin',
    1: 'admin',
}

interface User extends NameInfo {
    age: number,
}

const user1: User = {
    firstName: "t",
    lastName: "o",
    age: 11,
}
```

#### 函数

```typescript
let add: (x: number, y: number) => number

add = (arg1: 1, arg2: 2): number => arg1 + arg2

type Add = (x: number, y: number, z?: any) => number  // 类型别名

let addFunction = (x: number, y = 2) => x + y

let arr10 = [1, 2, 3]
let arr11 = [...arr10]

// 重载
function handleData(x: string): string[]
function handleData(x: number): number[]
function handleData(x: any): any {
    if (typeof x === "string") {
        return x.split('')
    } else {
        return x.toString().split('').map((item) => Number(item))
    }
}
```

#### 泛型

```typescript
const getArry = <T>(value: T, times: number = 5): T[] => {
    return new Array(times).fill(value)
}

getArry<number>(1234, 4).map((item) => item.toFixed())

const getArray1 = <T, U>(param1: T, param2: U, times: number): Array<[T, U]> => {
    return new Array(times).fill([param1, param2])
}
getArray1<number, string>(1, 'a', 3).forEach((item) => {
    console.log(item[0])
    console.log(item[1])
})

interface ValueWithLength {
    length: number
}

const getArray2 = <T extends ValueWithLength>(arg: T, times): T[] => {
    return new Array(times).fill(arg)
}
```
