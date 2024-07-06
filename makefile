default:
	g++ -Ofast main.cpp -o main -std=c++11 -I include -L lib -l SDL2-2.0.0

mac:
	g++ -Ofast main.cpp -o main -std=c++11 -I/opt/homebrew/include -L/opt/homebrew/lib -lSDL2

mac-static:
	g++ -Ofast main.cpp -o main -std=c++11 -I/opt/homebrew/include  -L/opt/homebrew/lib /opt/homebrew/lib/libSDL2.a -lm -liconv -Wl,-framework,CoreAudio -Wl,-framework,AudioToolbox -Wl,-weak_framework,CoreHaptics -Wl,-weak_framework,GameController -Wl,-framework,ForceFeedback -lobjc -Wl,-framework,CoreVideo -Wl,-framework,Cocoa -Wl,-framework,Carbon -Wl,-framework,IOKit -Wl,-weak_framework,QuartzCore -Wl,-weak_framework,Metal

clean:
	rm main
