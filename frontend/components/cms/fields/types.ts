export interface ModelField {
  name: string;
  verboseName: string;
  editable?: boolean;
  helpText?: string;
  type: string;
}

export type FieldProps = Omit<ModelField, "type">;

export interface BooleanFieldProps extends FieldProps {
  value?: boolean;
}

export interface TextFieldProps extends FieldProps {
  value?: string;
}

export interface CharFieldProps extends TextFieldProps {
  choices?: string[][]; // [["value", "Human-readable value"], ["a", "A"]]
}

export interface IntegerFieldProps extends FieldProps {
  value?: number;
  choices?: Array<string | number>[]; // [[0, "Zero"], [1, "One"]]
}
