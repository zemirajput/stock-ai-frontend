from app.preprocessing import prepare_input


X, df = prepare_input("BP.L")

print()

print("Input shape:")
print(X.shape)


print()

print(df.tail())