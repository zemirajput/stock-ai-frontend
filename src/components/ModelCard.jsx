function ModelCard({model, prediction, accuracy}){

return (

<div className="
bg-slate-800
rounded-xl
p-6
text-white
">

<h2 className="text-xl font-bold">
{model}
</h2>


<div className="mt-4">

<p className="text-gray-400">
Predicted Price
</p>

<p className="text-3xl font-bold">
${prediction}
</p>

</div>


<div className="mt-4">

<p className="text-gray-400">
Accuracy
</p>

<p className="text-green-400 text-xl">
{accuracy}%
</p>

</div>


</div>

)

}


export default ModelCard;
