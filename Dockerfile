#vincular imagen
FROM python:3.11-slim-bookworm

#crear direccion dentro del contenedor
WORKDIR /home/app

#copiar mi archivos a la direccion que le indique antes
COPY . /home/app

#instalar dependencias
RUN pip install -r requirements.txt

#exponer en el puerto 8000 porque mi app trabaja en ese puerto
EXPOSE 8000

#ejecutar en cmd para ejecutar proyecto
CMD ["uvicorn", "core.main:app", "--host", "0.0.0.0", "--port", "8000"]

#para crear la imagen usamos el comando docker build -t {nombre de la app}:{etiqueta que queramos} . (punto para indicarle que la ruta de la carpeta es esta)

#crear imagen
#guardar imagen en contenedor 
#ejecutar contenedor
#logs para confirmar