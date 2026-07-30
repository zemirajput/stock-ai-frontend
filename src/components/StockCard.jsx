function StockCard({title,value}){


return (

<div className="
bg-slate-800
text-white
rounded-xl
p-6
shadow-lg
">

<p className="text-gray-400">
{title}
</p>


<h2 className="text-3xl font-bold mt-3">
{value}
</h2>


</div>

)

}


export default StockCard;