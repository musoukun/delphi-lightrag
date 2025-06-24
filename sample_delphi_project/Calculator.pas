unit Calculator;

interface

uses
  System.SysUtils, System.Classes, Math;

type
  TCalculator = class
  private
    FLastResult: Double;
    FMemory: Double;
    FHistory: TStringList;
  public
    constructor Create;
    destructor Destroy; override;
    
    // 基本演算
    function Add(A, B: Double): Double;
    function Subtract(A, B: Double): Double;
    function Multiply(A, B: Double): Double;
    function Divide(A, B: Double): Double;
    
    // 高度な演算
    function Power(Base, Exponent: Double): Double;
    function SquareRoot(Value: Double): Double;
    function Logarithm(Value: Double): Double;
    function Sine(Angle: Double): Double;
    function Cosine(Angle: Double): Double;
    
    // メモリ機能
    procedure MemoryClear;
    procedure MemoryStore(Value: Double);
    procedure MemoryAdd(Value: Double);
    function MemoryRecall: Double;
    
    // プロパティ
    property LastResult: Double read FLastResult;
    property History: TStringList read FHistory;
  end;

  // エラークラス
  ECalculatorError = class(Exception);
  EDivisionByZero = class(ECalculatorError);
  EInvalidOperation = class(ECalculatorError);

implementation

{ TCalculator }

constructor TCalculator.Create;
begin
  inherited;
  FLastResult := 0;
  FMemory := 0;
  FHistory := TStringList.Create;
end;

destructor TCalculator.Destroy;
begin
  FHistory.Free;
  inherited;
end;

function TCalculator.Add(A, B: Double): Double;
begin
  Result := A + B;
  FLastResult := Result;
  FHistory.Add(Format('%f + %f = %f', [A, B, Result]));
end;

function TCalculator.Subtract(A, B: Double): Double;
begin
  Result := A - B;
  FLastResult := Result;
  FHistory.Add(Format('%f - %f = %f', [A, B, Result]));
end;

function TCalculator.Multiply(A, B: Double): Double;
begin
  Result := A * B;
  FLastResult := Result;
  FHistory.Add(Format('%f * %f = %f', [A, B, Result]));
end;

function TCalculator.Divide(A, B: Double): Double;
begin
  if B = 0 then
    raise EDivisionByZero.Create('Division by zero is not allowed');
    
  Result := A / B;
  FLastResult := Result;
  FHistory.Add(Format('%f / %f = %f', [A, B, Result]));
end;

function TCalculator.Power(Base, Exponent: Double): Double;
begin
  Result := Math.Power(Base, Exponent);
  FLastResult := Result;
  FHistory.Add(Format('%f ^ %f = %f', [Base, Exponent, Result]));
end;

function TCalculator.SquareRoot(Value: Double): Double;
begin
  if Value < 0 then
    raise EInvalidOperation.Create('Cannot calculate square root of negative number');
    
  Result := Sqrt(Value);
  FLastResult := Result;
  FHistory.Add(Format('√%f = %f', [Value, Result]));
end;

function TCalculator.Logarithm(Value: Double): Double;
begin
  if Value <= 0 then
    raise EInvalidOperation.Create('Logarithm is only defined for positive numbers');
    
  Result := Ln(Value);
  FLastResult := Result;
  FHistory.Add(Format('ln(%f) = %f', [Value, Result]));
end;

function TCalculator.Sine(Angle: Double): Double;
begin
  Result := Sin(Angle);
  FLastResult := Result;
  FHistory.Add(Format('sin(%f) = %f', [Angle, Result]));
end;

function TCalculator.Cosine(Angle: Double): Double;
begin
  Result := Cos(Angle);
  FLastResult := Result;
  FHistory.Add(Format('cos(%f) = %f', [Angle, Result]));
end;

procedure TCalculator.MemoryClear;
begin
  FMemory := 0;
  FHistory.Add('Memory cleared');
end;

procedure TCalculator.MemoryStore(Value: Double);
begin
  FMemory := Value;
  FHistory.Add(Format('Memory stored: %f', [Value]));
end;

procedure TCalculator.MemoryAdd(Value: Double);
begin
  FMemory := FMemory + Value;
  FHistory.Add(Format('Memory added: %f (total: %f)', [Value, FMemory]));
end;

function TCalculator.MemoryRecall: Double;
begin
  Result := FMemory;
  FHistory.Add(Format('Memory recalled: %f', [FMemory]));
end;

end.