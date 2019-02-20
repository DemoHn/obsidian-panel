package instance

import (
	"os"
	"strconv"
	"testing"
	"time"

	. "github.com/franela/goblin"
	"github.com/olebedev/emitter"
)

func TestEvent(t *testing.T) {
	g := Goblin(t)

	g.Describe("Instance > Event", func() {
		var inst *Instance
		var expID = 200
		// setup and teardown

		g.Before(func() {
			cwd, _ := os.Getwd()
			inst = New(cwd+"/../../bin/apm-test-helper", []string{"normal-run"}, false)
			inst.ID = expID
		})

		g.After(func() {
			inst.eventHandle.close()
		})

		g.It("should receive event: ActionStart", func() {
			var evtName string
			var evt emitter.Event
			var timeout = false
			go func() {
				inst.Start()
			}()
			defer inst.ForceStop()

			select {
			case evt = <-inst.Once(ActionError):
				evtName = ActionError
			case evt = <-inst.Once(ActionStart):
				evtName = ActionStart
			case <-time.After(3 * time.Second):
				timeout = true
			}

			g.Assert(timeout).Equal(false)
			g.Assert(evtName).Equal(ActionStart)
			g.Assert(evt.Int(0)).Equal(expID)
		})

		g.It("should receive event: ActionError (on start)", func() {
			newInst := New("./nonexistingcommand", []string{}, false)
			newInst.ID = 300

			var evtName string
			var evt emitter.Event
			var timeout = false
			go func() {
				newInst.Start()
			}()

			select {
			case evt = <-newInst.Once(ActionError):
				evtName = ActionError
			case evt = <-newInst.Once(ActionStart):
				evtName = ActionStart
			case evt = <-newInst.Once(ActionStart):
				evtName = ActionStop
			case <-time.After(3 * time.Second):
				timeout = true
			}
			g.Assert(timeout).Equal(false)
			// get error
			g.Assert(evtName).Equal(ActionError)
			g.Assert(evt.Int(0)).Equal(300)
			g.Assert(evt.String(1)).Equal(ActionStart)
		})

		g.It("should receive event: ActionStop (kill by signal)", func() {
			// consts
			const expExitCode = 23
			// vars
			var evtName string
			var evt emitter.Event
			var timeout = false

			cwd, _ := os.Getwd()
			nInst := New(cwd+"/../../bin/apm-test-helper", []string{"normal-run", strconv.Itoa(expExitCode)}, false)
			nInst.ID = 400

			go func() {
				nInst.Start()
			}()

			select {
			case evt = <-nInst.Once(ActionStart):
				// wait for a little time to warm up
				// and then send stop
				time.Sleep(100 * time.Millisecond)
				nInst.Stop(os.Interrupt)
			case <-time.After(3 * time.Second):
				timeout = true
			}

			select {
			case evt = <-nInst.Once(ActionStop):
				evtName = ActionStop
			case <-time.After(3 * time.Second):
				timeout = true
			}

			g.Assert(timeout).Equal(false)
			g.Assert(evtName).Equal(ActionStop)
			// instn ID
			g.Assert(evt.Int(0)).Equal(400)
			// exit code
			g.Assert(evt.Int(1)).Equal(expExitCode)
		})

		g.It("should receive event: ActionStop (stopped naturally)", func() {
			// consts
			const expExitCode = 20
			// vars
			var evtName string
			var evt emitter.Event
			var timeout = false

			cwd, _ := os.Getwd()
			nInst := New(cwd+"/../../bin/apm-test-helper", []string{"stop-on-time", "20", strconv.Itoa(expExitCode)}, false)
			nInst.ID = 401

			go func() {
				nInst.Start()
			}()

			select {
			case evt = <-nInst.Once(ActionStop):
				evtName = ActionStop
			case <-time.After(3 * time.Second):
				timeout = true
			}

			g.Assert(timeout).Equal(false)
			g.Assert(evtName).Equal(ActionStop)
			// instn ID
			g.Assert(evt.Int(0)).Equal(401)
			// exit code
			g.Assert(evt.Int(1)).Equal(expExitCode)
		})

		g.It("should receive event: ActionStop (exitCode = 0)", func() {
			// vars
			var evtName string
			var evt emitter.Event
			var timeout = false

			cwd, _ := os.Getwd()
			nInst := New(cwd+"/../../bin/apm-test-helper", []string{"stop-on-time", "20"}, false)
			nInst.ID = 402

			go func() {
				nInst.Start()
			}()

			select {
			case evt = <-nInst.Once(ActionStop):
				evtName = ActionStop
			case <-time.After(3 * time.Second):
				timeout = true
			}

			g.Assert(timeout).Equal(false)
			g.Assert(evtName).Equal(ActionStop)
			// instn ID
			g.Assert(evt.Int(0)).Equal(402)
			// exit code
			g.Assert(evt.Int(1)).Equal(0)
		})
	})
}
