npm install
cd ..
source venv/bin/activate
cd website/
npm run build
rm /usr/share/nginx/html/ -r
cp build /usr/share/nginx/html/ -r
