unit MainForm;

interface

uses
  System.SysUtils, System.Types, System.UITypes, System.Classes, System.Variants,
  FMX.Types, FMX.Controls, FMX.Forms, FMX.Graphics, FMX.Dialogs, FMX.StdCtrls,
  FMX.Edit, FMX.Controls.Presentation;

type
  TFormMain = class(TForm)
    ButtonCalculate: TButton;
    EditNumber1: TEdit;
    EditNumber2: TEdit;
    LabelResult: TLabel;
    procedure ButtonCalculateClick(Sender: TObject);
  private
    { Private declarations }
    function AddNumbers(A, B: Double): Double;
    function SubtractNumbers(A, B: Double): Double;
    function MultiplyNumbers(A, B: Double): Double;
    function DivideNumbers(A, B: Double): Double;
  public
    { Public declarations }
  end;

var
  FormMain: TFormMain;

implementation

{$R *.fmx}

procedure TFormMain.ButtonCalculateClick(Sender: TObject);
var
  Num1, Num2, Result: Double;
begin
  try
    Num1 := StrToFloat(EditNumber1.Text);
    Num2 := StrToFloat(EditNumber2.Text);
    Result := AddNumbers(Num1, Num2);
    LabelResult.Text := 'Result: ' + FloatToStr(Result);
  except
    on E: Exception do
      LabelResult.Text := 'Error: ' + E.Message;
  end;
end;

function TFormMain.AddNumbers(A, B: Double): Double;
begin
  Result := A + B;
end;

function TFormMain.SubtractNumbers(A, B: Double): Double;
begin
  Result := A - B;
end;

function TFormMain.MultiplyNumbers(A, B: Double): Double;
begin
  Result := A * B;
end;

function TFormMain.DivideNumbers(A, B: Double): Double;
begin
  if B <> 0 then
    Result := A / B
  else
    raise Exception.Create('Division by zero');
end;

end.