declare module "react-lines-ellipsis/lib/html" {
  import * as React from "react";

  interface ReactLinesEllipsisProps {
    basedOn?: "letters" | "words";
    className?: string;
    component?: string;
    ellipsis?: string;
    isClamped?: () => boolean;
    maxLine?: number | string;
    onReflow?: ({ clamped, text }: { clamped: boolean; text: string }) => any;
    style?: React.CSSProperties;
    text?: string;
    trimRight?: boolean;
    winWidth?: number;
  }

  class HTMLEllipsis extends React.Component<ReactLinesEllipsisProps> {
    static defaultProps?: ReactLinesEllipsisProps & {
      unsafeHTML: string;
    };
  }

  export default LinesEllipsis;
}
