object FormMain: TFormMain
  Left = 0
  Top = 0
  Caption = 'Calculator'
  ClientHeight = 400
  ClientWidth = 600
  FormFactor.Width = 320
  FormFactor.Height = 480
  FormFactor.Devices = [Desktop]
  DesignerMasterStyle = 0
  object EditNumber1: TEdit
    Touch.InteractiveGestures = [LongTap, DoubleTap]
    TabOrder = 0
    Position.X = 16.000000000000000000
    Position.Y = 24.000000000000000000
    Width = 200.000000000000000000
    Height = 32.000000000000000000
  end
  object EditNumber2: TEdit
    Touch.InteractiveGestures = [LongTap, DoubleTap]
    TabOrder = 1
    Position.X = 16.000000000000000000
    Position.Y = 64.000000000000000000
    Width = 200.000000000000000000
    Height = 32.000000000000000000
  end
  object ButtonCalculate: TButton
    Position.X = 16.000000000000000000
    Position.Y = 104.000000000000000000
    Width = 200.000000000000000000
    Height = 32.000000000000000000
    TabOrder = 2
    Text = 'Calculate'
    OnClick = ButtonCalculateClick
  end
  object LabelResult: TLabel
    Position.X = 16.000000000000000000
    Position.Y = 144.000000000000000000
    Width = 200.000000000000000000
    Height = 32.000000000000000000
    Text = 'Result:'
  end
end