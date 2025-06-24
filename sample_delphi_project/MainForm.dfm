object FormMain: TFormMain
  Left = 0
  Top = 0
  Caption = 'Calculator Application'
  ClientHeight = 400
  ClientWidth = 600
  Position = MainFormCenter
  FormFactor.Width = 320
  FormFactor.Height = 480
  FormFactor.Devices = [Desktop]
  OnCreate = FormCreate
  OnDestroy = FormDestroy
  DesignerMasterStyle = 0
  object EditDisplay: TEdit
    Touch.InteractiveGestures = [LongTap, DoubleTap]
    TabOrder = 0
    Position.X = 24.0
    Position.Y = 24.0
    Size.Width = 552.0
    Size.Height = 48.0
    Size.PlatformDefault = False
    TextSettings.Font.Size = 24.0
    TextSettings.HorzAlign = Trailing
    ReadOnly = True
    Text = '0'
  end
  object ButtonAdd: TButton
    Position.X = 24.0
    Position.Y = 96.0
    Size.Width = 80.0
    Size.Height = 40.0
    Size.PlatformDefault = False
    TabOrder = 1
    Text = '+'
    OnClick = ButtonOperationClick
  end
  object ButtonSubtract: TButton
    Position.X = 112.0
    Position.Y = 96.0
    Size.Width = 80.0
    Size.Height = 40.0
    Size.PlatformDefault = False
    TabOrder = 2
    Text = '-'
    OnClick = ButtonOperationClick
  end
  object ButtonMultiply: TButton
    Position.X = 200.0
    Position.Y = 96.0
    Size.Width = 80.0
    Size.Height = 40.0
    Size.PlatformDefault = False
    TabOrder = 3
    Text = '*'
    OnClick = ButtonOperationClick
  end
  object ButtonDivide: TButton
    Position.X = 288.0
    Position.Y = 96.0
    Size.Width = 80.0
    Size.Height = 40.0
    Size.PlatformDefault = False
    TabOrder = 4
    Text = '/'
    OnClick = ButtonOperationClick
  end
  object ButtonEquals: TButton
    Position.X = 376.0
    Position.Y = 96.0
    Size.Width = 80.0
    Size.Height = 40.0
    Size.PlatformDefault = False
    TabOrder = 5
    Text = '='
    OnClick = ButtonEqualsClick
  end
  object ButtonClear: TButton
    Position.X = 464.0
    Position.Y = 96.0
    Size.Width = 80.0
    Size.Height = 40.0
    Size.PlatformDefault = False
    TabOrder = 6
    Text = 'C'
    OnClick = ButtonClearClick
  end
  object EditHistory: TMemo
    Touch.InteractiveGestures = [Pan, LongTap, DoubleTap]
    DataDetectorTypes = []
    Position.X = 24.0
    Position.Y = 152.0
    Size.Width = 552.0
    Size.Height = 200.0
    Size.PlatformDefault = False
    TabOrder = 7
    Viewport.Width = 548.0
    Viewport.Height = 196.0
    ReadOnly = True
  end
  object LabelStatus: TLabel
    Position.X = 24.0
    Position.Y = 360.0
    Size.Width = 552.0
    Size.Height = 24.0
    Size.PlatformDefault = False
    Text = 'Ready'
    TabOrder = 8
  end
end