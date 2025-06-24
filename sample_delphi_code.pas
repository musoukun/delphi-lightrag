unit SampleUnit;

interface

uses
  System.SysUtils, System.Classes;

type
  TSampleClass = class(TObject)
  private
    FName: string;
    FValue: Integer;
    procedure SetName(const AName: string);
    function GetValue: Integer;
  public
    constructor Create;
    destructor Destroy; override;
    procedure ProcessData(const Input: string);
    function CalculateSum(A, B: Integer): Integer;
    property Name: string read FName write SetName;
    property Value: Integer read GetValue;
  end;

  THelperClass = class
  private
    FItems: TStringList;
  public
    constructor Create;
    destructor Destroy; override;
    procedure AddItem(const Item: string);
    function GetItemCount: Integer;
  end;

implementation

{ TSampleClass }

constructor TSampleClass.Create;
begin
  inherited;
  FName := 'Default';
  FValue := 0;
end;

destructor TSampleClass.Destroy;
begin
  inherited;
end;

procedure TSampleClass.SetName(const AName: string);
begin
  if AName <> FName then
    FName := AName;
end;

function TSampleClass.GetValue: Integer;
begin
  Result := FValue;
end;

procedure TSampleClass.ProcessData(const Input: string);
var
  I: Integer;
begin
  for I := 1 to Length(Input) do
  begin
    Inc(FValue, Ord(Input[I]));
  end;
end;

function TSampleClass.CalculateSum(A, B: Integer): Integer;
begin
  Result := A + B;
end;

{ THelperClass }

constructor THelperClass.Create;
begin
  inherited;
  FItems := TStringList.Create;
end;

destructor THelperClass.Destroy;
begin
  FItems.Free;
  inherited;
end;

procedure THelperClass.AddItem(const Item: string);
begin
  FItems.Add(Item);
end;

function THelperClass.GetItemCount: Integer;
begin
  Result := FItems.Count;
end;

end.