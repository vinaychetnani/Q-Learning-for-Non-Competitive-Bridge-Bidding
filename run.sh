echo "Number of Samples Generated"
ta -hu $USER /home
count=10
echo $((16 * $count))
echo "Compiling DDS Library"
cd GeneratingData/dds/src
make
cd ../../.. 
echo "Copying Library File"
cp GeneratingData/dds/src/libdds.a GeneratingData
echo "Compiling"
g++ -O3 -mtune=generic -fopenmp -c ./GeneratingData/DoubleDummy.cpp -o./GeneratingData/DoubleDummy.o
g++ -O3 -mtune=generic -fopenmp  ./GeneratingData/DoubleDummy.o -L. -ldds -o ./GeneratingData/DoubleDummy
echo "Making Data Directory"
[ -d Data ]&&echo "Exists"||mkdir Data
echo "Copying Executable"
for i in {0..15}; do cp GeneratingData/DoubleDummy Data/$i; done
echo "Generating Double Dummy Hands and Tricks"
for i in {0..15}; do ./Data/$i $(($i * $count)) $count > ./Data/Data-$i.raw & done
echo "Deleting Executables"
for i in {0..15}; do rm Data/$i; done
echo "Cleaning Double Dummy Hands and Tricks"
for i in {0..15}; do echo $i; python GeneratingData/CleanDoubleDummy.py Data/Data-$i.raw Data/Data-$i.clean; done
echo "Scoring Hands"
for i in {0..15}; do echo $i; python GeneratingData/ScoreDoubleDummy.py Data/Data-$i.clean Data/Data-$i.score; done
echo "Vectorising Hands"
for i in {0..15}; do echo $i; python GeneratingData/VectoriseDoubleDummy.py Data/Data-$i.score Data/Data-$i.npy; done
echo "Displaying Sample Output"
python GeneratingData/Sample.py Data/Data-0.score
